# Example

Follows an example folder about how-to organize the subsite template folder to be able to have a custom template for each subsite.

## Folder structure

- The folder name **MUST** match the subsite slug defined via django-admin page
- The folder structure must match the one normally created for an override.

For example, let's assume that we want to override the "topbar.html" for a specific subsite named `subsite_1`

The folder structure must match the one normally used for an override, The template folder inside the path subsites/templates should look similar to this one

```bash
.
└── subsite_1
    └── geonode-mapstore-client
        └── snippets
            └── topbar.html
```
