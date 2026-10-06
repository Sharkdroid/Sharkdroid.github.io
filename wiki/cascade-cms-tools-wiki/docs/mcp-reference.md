# MCP Server Reference

Read-only tools exposed by `cascade-cms-rest-mcp`. Requires
`CASCADE_API_KEY` and `CASCADE_URL` environment variables.

---

## cascade_search

```python
cascade_search(query: str, site: str, asset_types: list[str] | None = None, limit: int | None = None) -> dict[str, Any]
```

Searches a site for assets by text and returns the id, type, path, and name of each match.

---

## cascade_read_asset

```python
cascade_read_asset(identifier: IdentifierType | CascadePath, format: Literal['concise', 'detailed'] = 'concise') -> dict[str, Any]
```

Reads one asset, addressed either by id and type or by site, path, and type.

---

## cascade_query_asset

```python
cascade_query_asset(identifier: IdentifierType | CascadePath, query: str, format: Literal['concise', 'detailed'] = 'concise', limit: int | None = None) -> dict[str, Any]
```

Returns one narrowed part of an asset selected by a small path query, and works on any asset type rather than only data-bound ones.

---

## cascade_get_data_structure

```python
cascade_get_data_structure(identifier: IdentifierType | CascadePath, group: str, node_identifier: str | None = None, limit: int | None = None) -> dict[str, Any]
```

Returns the field schema of one group on a data-bound asset, resolved from its bound content type or data definition rather than sampled from the asset itself.

---

## cascade_get_page_config

```python
cascade_get_page_config(identifier: IdentifierType | CascadePath, configuration_name: str | None = None, page_region: str | None = None, limit: int | None = None) -> dict[str, Any]
```

Returns a data-bound asset's page configuration names from its bound content type, plus the region content of one configuration on that asset.

---

## cascade_root_container_id

```python
cascade_root_container_id(site_identifier: IdentifierType | CascadePath, asset_type: Literal['datadefinition', 'sharedfield', 'folder']) -> dict[str, Any]
```

Returns the top-level container id for data definitions, shared fields, or folders on a site, as a starting point for browsing that tree.

---

## cascade_list_sites

```python
cascade_list_sites(limit: int | None = None) -> dict[str, Any]
```

Lists every site on the Cascade server.
