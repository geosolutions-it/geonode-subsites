# geonode-subsites

Enable the possibility to have subsites in GeoNode.

The subsite is virtual so no additional code is needed to setup the subsites

# Installation
Add in the geonode settings the following code

```
ENABLE_SUBSITE_CUSTOM_THEMES = True
SUBSITE_READ_ONLY = True / False
INSTALLED_APPS += ("subsites",)
```

`ENABLE_SUBSITE_CUSTOM_THEMES:` Enable the subsite login inside the app
`SUBSITE_READ_ONLY:` make the subsites read-only for all the users


## How to configure a subsite

The subsite are configurable ONLY via django admin

- Open to `http://{host}/admin`
- Navigate to the `Subsite` module
- Top-right click on `Add new sub site`

The information must be filled as follows:

- `Slug name` an unique identifier. This is going to be used as path to navigate to the subsite. For example:
```python
Slug => subsite_1

subsite_url => `http://{host}/subsite_1/`

Slug => italy

subsite_url => `http://{host}/italy/`

```

- `Theme`: Customized geonode theme to be used under the subsite. see `GeoNodeThemeCustomization` for more information


- `Region`, `Category`, `Groups`, `Keyword`: In this fields is possible to select multiple field. 
**NOTE**: This fields have a specific use. If selected, the search result for the subsite are going to be *pre-filtered* by this values.

The above fiter works in **OR** if multuple field of the same kind are selected, and in **AND** between all the filters:

```
(category==x || category==y || ...) && (keyword==x || keyword==y || ...) && (region==x|| region==y|| ...)
```

For example 1:

```
Keyword selected for subsite1 -> key1 means that only the resources with associated the keyword `key1` are going to be returned
```
Example 2
```
Keyword selected for subsite1 -> key1
Region selected for subsite1 -> Italy
means that only the resources with associated the keyword `key1` and as region `Italy` are going to be returned
```