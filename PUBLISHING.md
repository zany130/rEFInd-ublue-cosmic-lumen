# GitHub publishing

1. Boot-test the theme and keep it marked beta until the layout is verified at actual rEFInd resolution.
2. Confirm permissions for any user-supplied imagery/trademarks before public redistribution.
3. Create an empty GitHub repository, e.g. `zany130/rEFInd-ublue-cosmic-lumen` (unofficial, not endorsed by Universal Blue).
4. Unzip the **source** ZIP, `cd rEFInd-ublue-cosmic-lumen`, then:

```sh
git init -b main
git add .
git commit -m "Initial Universal Blue Cosmic Lumen theme (beta)"
git remote add origin https://github.com/zany130/rEFInd-ublue-cosmic-lumen.git
git push -u origin main
```

Do not publish the install ZIP as a stable release before actual firmware testing. When ready, add a release with the install ZIP attached.
