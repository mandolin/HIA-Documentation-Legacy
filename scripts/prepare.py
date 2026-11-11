"""验证并展开已发布的参考快照。 Verify and unpack a previously published reference snapshot."""

import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile
import tempfile


def require(condition, message):
    """遇到不符合清单的输入立即停止。 Stop on input that disagrees with the snapshot."""
    if not condition:
        raise ValueError(message)


def digest(file):
    """流式核验文件摘要。 Hash a file without loading it into memory."""
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare(snapshot, archive, output):
    """核验摘要、成员、来源和旧索引后展开普通文件。 Verify digests, members, provenance, and index before unpacking ordinary files."""
    require(not output.exists() and not output.is_symlink(), 'Output already exists.')
    require(snapshot['tarBytes'] <= 2 * 1024**3 and snapshot['bytes'] <= 1_000_000_000 and snapshot['files'] <= 100_000, 'Snapshot exceeds the supported budget.')
    require(digest(archive) == snapshot['gzipSha256'], 'Compressed snapshot digest mismatch.')
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        tar_path = Path(scratch) / 'verified.tar'
        with gzip.open(archive, 'rb') as source, tar_path.open('wb') as destination:
            remaining = snapshot['tarBytes']
            while remaining:
                block = source.read(min(remaining, 1024**2))
                require(block, 'Truncated snapshot.')
                destination.write(block)
                remaining -= len(block)
            require(not source.read(1), 'Expanded snapshot exceeds its declared size.')
        require(digest(tar_path) == snapshot['tarSha256'], 'Snapshot TAR digest mismatch.')

        with tarfile.open(tar_path, 'r:') as bundle:
            files = {}
            for member in bundle:
                name = member.name.removeprefix('./')
                if member.isdir() and name in ('', '.'):
                    continue
                route = PurePosixPath(name)
                require(name == route.as_posix() and not route.is_absolute() and '..' not in route.parts and not any(char in name for char in '\\:%?#'), 'Invalid archive path.')
                require(all(not part.startswith('.') or part == '.nojekyll' for part in route.parts), 'Unexpected hidden path.')
                if member.isdir():
                    continue
                require(member.isfile() and name not in files, 'Expected unique ordinary files.')
                files[name] = member
            require(len(files) == snapshot['files'] and sum(member.size for member in files.values()) == snapshot['bytes'], 'Unexpected file totals.')
            index = json.load(bundle.extractfile(files['versions.json']))
            provenance = json.load(bundle.extractfile(files['reference-build.json']))
            require(index.get('contract') == 'hia-reference-version-index' and index.get('contractVersion') == '0.1.0-draft' and index['versioning']['compatibilityAliases']['root'] == 'current', 'Unexpected legacy index.')
            require(provenance['privacy']['status'] == 'pass' and provenance['privacy']['sourcesContentPolicy'] == 'none', 'Unexpected source policy.')
            require(any(source['repository'] == snapshot['repository'] and source['commit'] == snapshot['commit'] for source in provenance['sources']), 'Unexpected source revision.')
            require(all(partition['projectIndex'] in files for partition in index['versioning']['searchPartitions']), 'Missing search partition.')

            # <lang zh-CN>仅复制已枚举的普通文件正文，忽略归档权限和其他文件元数据。</lang><lang en>Copy only inventoried regular-file bodies, ignoring archive permissions and other file metadata.</lang>
            stage = Path(scratch) / 'site'
            stage.mkdir()
            for name, member in files.items():
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, target.open('xb') as destination:
                    shutil.copyfileobj(source, destination)
            stage.rename(output)
    print(f'Validated {snapshot["files"]} files and {snapshot["bytes"]} bytes at {snapshot["commit"]}.')


if __name__ == '__main__':
    manifest, archive_path, output_path = map(Path, sys.argv[1:])
    prepare(json.loads(manifest.read_text(encoding='utf-8')), archive_path, output_path)
