# HIA Documentation System legacy reference

This repository hosts the compatibility reference site at [HIA Documentation Legacy](https://mandolin.github.io/HIA-Documentation-Legacy/). Machine clients can read the [legacy version index](https://mandolin.github.io/HIA-Documentation-Legacy/versions.json) with the `hia-reference-version-index@0.1.0-draft` reader. Resolve index paths relative to the returned index URL.

The site deploys a complete previously published HIA Documentation System Pages artifact. `snapshot.json` identifies its upstream commit, successful run, archive checksums and expected file totals. The tagged release stores the verified archive, and the deploy workflow verifies and extracts it before publishing. To roll back, dispatch the workflow at the deployment commit that selects the earlier snapshot. The archived reference assets keep their original licenses.
