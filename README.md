# geonode-subsites

Enable the possibility to have subsites in GeoNode.

The subsite is virtual so no additional code is needed to setup the subsites

# Installation
Add in the geonode settings the following code

```
ENABLE_SUBSITE_CUSTOM_THEMES = True
INSTALLED_APPS += ("subsites",)
ENABLE_CATALOG_HOME_REDIRECTS_TO = False
SUBSITE_READ_ONLY = True/False # return download_resourcebase and view resourcebase as permissions
```

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

## Exclusive keyword

During the app initialization the subsite will automatically generate a keyword named `subsite_exclusive`. Each resource with this keyword assigned, will be escluded from the global catalogue (this is valid also for the API/v2 `/resources`, `/datasets`, `/documents`, `/maps`, `/geoapps` )

**NOTE:** The `subsite_exclusive` keyword is used to exclude a resource from the global catalog. This keyword is commonly applied to all resources. If a resource needs to be accessible only within a specific subsite, utilize the additional configuration provided by that subsite to filter it out from other subsites.

For example:

```
resource1 -> no keyword
resource2 -> keyword1 assinged
resource3 -> subsite_exclusive keyword assigned

Call -> http://localhost:8000/#/
    - will return resource1 and resource2
```

Via API/v2 `/resources`, `/datasets`, `/documents`, `/maps`, `/geoapps` is possible to return all the value even if the `subsite_exclusive` keyword is set
For example:

```
resource1 -> no keyword
resource2 -> keyword1 assinged
resource3 -> subsite_exclusive keyword assigned

Call -> http://localhost:8000/api/v2/resources/
    - will return resource1 and resource2

    
Call -> http://localhost:8000/api/v2/resources/?return_all=true
    - will return resource1, resource2 and resource3
```


# Override Subsite template

Follows an example folder about how-to organize the subsite template folder to be able to have a custom template for each subsite.

## Folder structure

- The folder name **MUST** match the subsite slug defined via django-admin page
- The folder structure must match the one normally created for an override.

For example, let's assume that we want to override the `topbar.html` for a specific subsite named `subsite_1` and `subsite_2`

The folder structure must match the one normally used for an override, The template folder inside the path subsites/templates should look similar to this one

```bash
.
└── subsite_1
    └── geonode-mapstore-client
        └── snippets
            └── topbar.html
└── subsite_2
    └── geonode-mapstore-client
        └── snippets
            └── topbar.html        
```

## Global override

The code offers also the possibility to globally override the code for the subsites.

To do it, is enough to place the file in the main `templates` folder of the app outside from any subsite directory.


## Example 
```bash
templates
├── geonode-mapstore-client
│   ├── _geonode_config.html
│   ├── index.html
│   └── snippets
│       ├── brand_navbar.html
│       ├── search_bar.html
│       └── topbar.html
├── subsites
├───── common
│       └── geonode-mapstore-client
│       └── snippets
│           └── topbar.html
├───── subsite_1
       └── geonode-mapstore-client
       └── snippets
          └── topbar.html

```

The example above:
- **ALL** the subsite will use the override templates available under the `geonode-mapstore-client` table under the root `templates`
- `subsite_1` will get the `topbar.html` from it's specific subsite template folder
- All the other templates are taken by the common folder if the filw is available otherwise from the default dirs

## Let a spefici URLs use the 

Subsite doesnt follow the default django "render" function since we have to handle the template dirs dinamically.

To let a specific urls works with this system (example profile, metadata etc..)

1) register the URL in the `subsites/urls.py`
example 

```python
re_path(r"^(?P<subsite>[^/]*)", views.subsite_home, name="subsite_home")
```

2) Define the function in `views.py`

```python
def subsite_home(request, subsite):
    slug = extract_subsite_slug_from_request(request, return_object=False)
    if not slug:
        raise Http404

    return subsite_render(request, "index.html", slug=slug)
```

The function requires 3 parameters:

- `request`: Request object, easily obtainable by the view param
- `template_name`: name of the html file to render example `index.html`
- `slug`: The subsite slug. Can be obtained by the request object using the utility function `extract_subsite_slug_from_request`


