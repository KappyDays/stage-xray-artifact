# Publication-safe data dictionary

## Scientific record

Each selected Prim is represented by four ordered fields:

| Field | Type | Meaning |
|---|---|---|
| `prim_path` | string | Pair-stable hierarchy token used as the selected record key |
| `prim_type_name` | string | OpenUSD Prim type name observed under the fixed extraction conditions |
| `has_authored_references` | `true` / `false` | Whether the Prim has directly authored Reference metadata |
| `has_authored_payloads` | `true` / `false` | Whether the Prim has directly authored Payload metadata |

The CSV-only `path_encoding` column is metadata, not a fifth scientific field.
Its required value is `PAIR_HIERARCHY_TOKEN_V1`.

## Path encoding

Public paths have the grammar:

```text
/SCALEX_POD(?:/Ndddd)*
```

where each `dddd` is four decimal digits. Tokens are stable within this
Earlier/Later pair and preserve parent-child shape. They are not globally
stable identifiers, physical asset identities, or reversible encodings.

## Difference types

The four fields yield five possible difference types:

1. `ADDED`
2. `REMOVED`
3. `TYPE_CHANGED`
4. `REFERENCE_PRESENCE_CHANGED`
5. `PAYLOAD_PRESENCE_CHANGED`

Only `ADDED` and `REMOVED` are nonzero in the evaluated pair. Synthetic tests
exercise the other three difference types.

The v4 output schema retains `false_positive_path_count` for compatibility.
In the final manuscript terminology, a false-positive recomputed result is an
`extra` difference.

## Region terminology

- A landmark is a selected Prim with authored Reference or Payload presence.
- Each selected Prim belongs to its nearest ancestor-or-self landmark.
- A nested landmark starts its own region and is excluded from its ancestor's
  membership.
- If no landmark owns a path, it belongs to one scope-local residual region.
- The union of landmark paths from both states identifies the regions; the
  same landmark path identifies the same region on both comparison sides.
- An `affected region` has added, removed, or changed status. Only the single
  region whose records differ on both sides is called a `changed region` for
  this pair.
