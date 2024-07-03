# meles

meles are the zoological family of the badgers. 

So meles creates badges for you. Even in isolated environments.

Currently, raw shields are supported as well as the nuget-api.

meles hereby tries to be as compatible as necessary the original shields.io API.

## Endpoints

Currently, the following end-points are available:

### Shields

Supports the [shields.io](https://shields.io/badges) static badge.

Supported parameters:
  * badgeContent
  * logo
  * logoColor
  * label
  * labelColor
  * color
  * cacheSeconds

### NuGet

Supports the [shields.io](https://shields.io/) dynamic badges. The following routes are supported:
  * [version](https://shields.io/badges/nu-get-version): variant: v
  * [version-preview](https://shields.io/badges/nu-get-version): variant: vpre
  * [downloads](https://shields.io/badges/nu-get-downloads)

Supported parameters:
  * label
  * labelColor
  * color
  * cacheSeconds

### Dynamic

Supports the [shields.io](https://shields.io/) dynamic badges. The following routes are supported:
  * [Dynamic JSON](https://shields.io/badges/dynamic-json-badge)
  * [Dynamic YAML](https://shields.io/badges/dynamic-yaml-badge)
  * [Dynamic TOML](https://shields.io/badges/dynamic-toml-badge)
  * [Dynamic XML](https://shields.io/badges/dynamic-xml-badge)
  * [Endpoint](https://shields.io/badges/endpoint)

Supported parameters:
  * url
  * query
  * logo
  * logoColor
  * label
  * labelColor
  * color
  * prefix
  * suffix
  * cacheSeconds

### System

**/health**: 
   A health resource. Returns `OK`.
   Can be disabled by setting `MELES_USE_HEALTHCHECK` to `False`

**/metrics**:
   An open metrics compliant endpoint for [prometheus](https://prometheus.io) scraping.
   Can be disabled by setting `MELES_USE_PROMETHEUS` to `False`

**/system**:
   Returns a JSON file with information about this package.

## Configuration

The configuration takes place using the following environment variables:

| Environment Variables      | Values / Ranges         | Descriptions                                                                                                                                                          |
|----------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MELES_PORT                 | ushort                  | Port, only used for `python -m`                                                                                                                                       |
| MELES_HOST                 | IP-Address / FQDN       | Host, only used for `python -m`                                                                                                                                       |
| MELES_CONFIGURATION_MODULE | string                  | Setup method in pkg_resource notation                                                                                                                                 |
| MELES_CACHE_*              | individual              | Key-Value-Pairs to configure [falcon-caching](https://falcon-caching.readthedocs.io/en/latest/#configuring-falcon-caching). Just add `MELES_` to get the config value |
| MELES_USE_HEALTHCHECK      | True, False             | Enable or disable health-check endpoint                                                                                                                               |
| MELES_USE_PROMETHEUS       | True, False             | Enable or disable prometheus metrics endpoint                                                                                                                         |
| MELES_ENVIRONMENT          | PRODUCTION, DEVELOPMENT | Development to use                                                                                                                                                    |

When Environment is set to `DEVELOPMENT`, the logging level will be set to Debug, otherwise Info will be used.

All logging will be formatted in a structured manner using a JSON representation and printed to stderr, which should not interfere with WSGI.

## Documentation

Refer to [docs](./docs/ReadMe.md) for details.
