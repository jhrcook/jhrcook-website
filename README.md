# Personal Website

[![Deploy Hugo site to Pages](https://github.com/jhrcook/jhrcook-website/actions/workflows/gh-pages.yaml/badge.svg)](https://github.com/jhrcook/jhrcook-website/actions/workflows/gh-pages.yaml)

Built with [Hugo](https://gohugo.io) using the [Blowfish](https://blowfish.page) theme.

To-Do:

- [x] Copy over blog posts
  - [x] Copy over posts and get Hugo running
  - [x] Check styling of all posts
  - [x] Align on tags and categories
  - [x] Make "Series" of some of the posts:
    - [x] Riddlers
    - [x] PyMC Splines
  - [x] Reduce image/asset sizes (2019-08-14_plants-led-light)
- [ ] Add to Hobbies
  - [ ] backpacking
  - [ ] bread
  - [ ] fishing
  - [ ] plants
  - [x] reading
  - [x] running
- [ ] Move over Projects
- [ ] Add CV somewhere
- [ ] Add text to "About" page

---

## Notes

### Initial creation

Steps for creating website:

```bash
hugo new site jhrcook-website
cd jhrcook-website
git init
```

Blowfish theme:

```bash
git submodule add -b main https://github.com/nunocoracao/blowfish.git themes/blowfish

```

### Updating

#### Blowfish theme

For updating ([instructions](https://blowfish.page/docs/installation/#installing-updates))

```bash
git submodule update --remote --merge
```

Can find the maximum Hugo version in the file [./themes/blowfish/config.toml](./themes/blowfish/config.toml).

Can then install this version of Hugo with the following steps:

1. Download the release from here: <https://github.com/gohugoio/hugo/releases>
2. Extract
3. Move the `hugo` executable to `~/.local/bin/`
4. May need to all use of the downloaded binary in System Settings/Security

Finally, set the desired version of Hugo in the [netlify.toml](./netlify.toml) and GitHub Actions [workflow](.github/workflows/gh-pages.yaml)
