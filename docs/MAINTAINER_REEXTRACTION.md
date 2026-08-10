# Maintainer-only re-extraction tier

This procedure is intentionally not part of the public replay.

The measured projections were extracted with NVIDIA Isaac Sim 6.0.0 full Kit,
internal build `6.0.0-rc.59+release.41464.5f2772bc.gl`, bundled OpenUSD 0.25.11,
`LoadAll`, no population mask, an implicit empty session layer, no variant
override or post-open mutation, default-predicate traversal, and no
instance-proxy expansion.

Authorized maintainers need the exact Earlier/Later Stage roots, all dependent
assets, the private resolver configuration, and the frozen input commitments.
They must use a new non-overwriting output directory and compare resulting
projection hashes with the publication record. A new extraction is a new
measurement and must not overwrite this release.
