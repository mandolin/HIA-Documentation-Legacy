# HIA Documentation System legacy reference

This repository hosts the compatibility reference site at [HIA Documentation Legacy](https://mandolin.github.io/HIA-Documentation-Legacy/). Machine clients can read the [legacy version index](https://mandolin.github.io/HIA-Documentation-Legacy/versions.json) with the `hia-reference-version-index@0.1.0-draft` reader. Resolve index paths relative to the returned index URL.

The site deploys a complete previously published HIA Documentation System Pages artifact. `snapshot.json` identifies its upstream commit, successful run, archive checksums and expected file totals. The tagged release stores the verified archive, and the deploy workflow verifies and extracts it before publishing. To roll back, dispatch the workflow at the deployment commit that selects the earlier snapshot. The archived reference assets keep their original licenses.

The selected compatibility snapshot is source `6ed04c9b029a00307090e18d8acd2552e820f6b0`, from successful upstream run `43385303181`. It contains 77,940 files and 992,538,326 expanded bytes. Its original index and root are paired with the official website composition by SHA-256.

中文。当前兼容选择为该成功工件的完整原件，旧索引和根页面通过SHA-256与官网装配配对。
