# Changelog

## [0.5.0](https://github.com/wardensfx/OuyouyouTube/compare/v0.4.1...v0.5.0) (2026-07-05)


### New Features 🎉

* **front:** view the changelog from the sidebar's version number ([a34e3eb](https://github.com/wardensfx/OuyouyouTube/commit/a34e3eb759c93ed28ded60c4f02954e45c8ea395))
* paginate favorites/trending/channel-videos/search with infinite scroll ([#74](https://github.com/wardensfx/OuyouyouTube/issues/74), [#78](https://github.com/wardensfx/OuyouyouTube/issues/78)) ([7d01517](https://github.com/wardensfx/OuyouyouTube/commit/7d01517839e4df7aec5774b8a58fb4c8c8d94b40))
* **server:** add optional Google account allowlist ([#84](https://github.com/wardensfx/OuyouyouTube/issues/84)) ([2334030](https://github.com/wardensfx/OuyouyouTube/commit/2334030de019db35340b22bc04f4806e9c7dea48))
* **server:** paginate playlist items with full-load fallback for sort/filter ([#78](https://github.com/wardensfx/OuyouyouTube/issues/78)) ([08c4253](https://github.com/wardensfx/OuyouyouTube/commit/08c4253b6cf21153a10b758d11b17753ac2e5917))


### Bug Fixes 🐛

* 74-[#77](https://github.com/wardensfx/OuyouyouTube/issues/77) + scoped pagination for [#78](https://github.com/wardensfx/OuyouyouTube/issues/78) ([89f8c11](https://github.com/wardensfx/OuyouyouTube/commit/89f8c11551a7123348b3cb3baa0e106a82eeebb0))
* **deploy:** bind Redis port to loopback only in docker-compose ([#85](https://github.com/wardensfx/OuyouyouTube/issues/85)) ([a438b91](https://github.com/wardensfx/OuyouyouTube/commit/a438b9158e997d0b4fd16f713d66b7fcef4fc232))
* **front:** add keyboard escape, focus handling, and dialog semantics to overlays ([#91](https://github.com/wardensfx/OuyouyouTube/issues/91)) ([999489b](https://github.com/wardensfx/OuyouyouTube/commit/999489badf3c88e5c429ce0fa9a4687d5c4c611d))
* **front:** add min-width:0 to PlaylistCard's .card to prevent grid overflow ([#94](https://github.com/wardensfx/OuyouyouTube/issues/94)) ([4ab7603](https://github.com/wardensfx/OuyouyouTube/commit/4ab7603d34a5936e44aefc53ce5690e5ce4e796d))
* **front:** bring Channel.vue and History.vue in line with standard states ([#97](https://github.com/wardensfx/OuyouyouTube/issues/97)) ([70b1b48](https://github.com/wardensfx/OuyouyouTube/commit/70b1b4813a365984e6a481efca4e26fe164ef41e))
* **front:** bundle of small CSS/formatting fixes ([#99](https://github.com/wardensfx/OuyouyouTube/issues/99)) ([1d2f745](https://github.com/wardensfx/OuyouyouTube/commit/1d2f74540ed1481494a32ea03dc0a765789b4f76))
* **front:** correct like button state outside loaded favorites pages ([#87](https://github.com/wardensfx/OuyouyouTube/issues/87)) ([5421003](https://github.com/wardensfx/OuyouyouTube/commit/5421003668b58f2096d745503cff06e4d6c6e2d6))
* **front:** enlarge icon-button touch targets and add missing labels ([#93](https://github.com/wardensfx/OuyouyouTube/issues/93)) ([b449e4a](https://github.com/wardensfx/OuyouyouTube/commit/b449e4ae03a576dba7255cff5aeca525cf87c2f5))
* **front:** improve accent button text contrast to meet WCAG AA ([#96](https://github.com/wardensfx/OuyouyouTube/issues/96)) ([5edaca7](https://github.com/wardensfx/OuyouyouTube/commit/5edaca708bfadc8dca8a45981dca92ea4da9d999))
* **front:** improve PlaylistDetail sort-switch full-load feedback ([#95](https://github.com/wardensfx/OuyouyouTube/issues/95)) ([7dab6cf](https://github.com/wardensfx/OuyouyouTube/commit/7dab6cf5e150bb4bc354f7da2adc3d72c8b5c8b9))
* **front:** resolve grid overflow, stale iOS PWA installs, and pull-to-refresh rubber-band ([#74](https://github.com/wardensfx/OuyouyouTube/issues/74), [#75](https://github.com/wardensfx/OuyouyouTube/issues/75), [#76](https://github.com/wardensfx/OuyouyouTube/issues/76), [#77](https://github.com/wardensfx/OuyouyouTube/issues/77)) ([3edfc77](https://github.com/wardensfx/OuyouyouTube/commit/3edfc7712a65f8ce6dbc10c0dd281e6ef667691c))
* **front:** standardize on "Vidéos aimées" for the liked-videos feature ([#98](https://github.com/wardensfx/OuyouyouTube/issues/98)) ([8f339eb](https://github.com/wardensfx/OuyouyouTube/commit/8f339eb89c6ec3fb776ea7aa513a139274d2053c))
* **front:** stop nesting interactive buttons inside VideoCard's RouterLink ([#92](https://github.com/wardensfx/OuyouyouTube/issues/92)) ([f790dbd](https://github.com/wardensfx/OuyouyouTube/commit/f790dbd0f597323f823fb5a3f9e7e5a0c5179773))
* **front:** surface silent pagination errors with loading indicators and retry ([#88](https://github.com/wardensfx/OuyouyouTube/issues/88)) ([cdb808e](https://github.com/wardensfx/OuyouyouTube/commit/cdb808e3a7a22744d29d0baef541b68e333b3e9c))
* **server:** partition playlist_items/video_details cache by account_id ([#82](https://github.com/wardensfx/OuyouyouTube/issues/82)) ([c3308d0](https://github.com/wardensfx/OuyouyouTube/commit/c3308d0769ed913ce4b297a43d6b6f9512dbf6b8))
* **server:** purge and revoke OAuth tokens when unlinking an account ([#83](https://github.com/wardensfx/OuyouyouTube/issues/83)) ([efd28e3](https://github.com/wardensfx/OuyouyouTube/commit/efd28e3cdeb2d82a6cde16a264ba02de3997bfeb))
* **server:** validate playlist_id/item_id to prevent glob injection in cache invalidation ([#86](https://github.com/wardensfx/OuyouyouTube/issues/86)) ([02a9a15](https://github.com/wardensfx/OuyouyouTube/commit/02a9a151e075551834387d48f333b90fa15eaae9))


### Documentation 📝

* catch up ROADMAP.md, CLAUDE.md structure, and README credits/env docs ([edfb1ea](https://github.com/wardensfx/OuyouyouTube/commit/edfb1ea3c30aa3aff8ed8d23ffaa9c798f18a737))
* make Conventional Commits mandatory and unmissable in CLAUDE.md ([5ec153f](https://github.com/wardensfx/OuyouyouTube/commit/5ec153fe993ee4ba36869b4b0095ba76510ea29e))


### Other Changes

* **front:** extract shared usePaginatedList composable ([#89](https://github.com/wardensfx/OuyouyouTube/issues/89)) ([4dde492](https://github.com/wardensfx/OuyouyouTube/commit/4dde4929679243818ad85c8b4a346e562d1fb971))

## [0.4.1](https://github.com/wardensfx/OuyouyouTube/compare/v0.4.0...v0.4.1) (2026-07-05)


### Bug Fixes 🐛

* **front:** recette batch — account switcher dismiss, media session, description scroll ([5d5f33c](https://github.com/wardensfx/OuyouyouTube/commit/5d5f33cf23217c7cff4fa3cbe91f3da480916821))
* **front:** three PWA feel issues (overscroll, modal position, input zoom) ([5a199ab](https://github.com/wardensfx/OuyouyouTube/commit/5a199ab75ba5b92a7d733d48c9c998dc467980fa))
* **front:** unbroken long text (e.g. URLs) overflowing and skewing layout ([c727e32](https://github.com/wardensfx/OuyouyouTube/commit/c727e32edce92a3220b6e26a72a5d70001d5fdeb))

## [0.4.0](https://github.com/wardensfx/OuyouyouTube/compare/v0.3.0...v0.4.0) (2026-07-05)


### New Features 🎉

* **front:** overlay VideoCard actions on the thumbnail instead of a row below it ([06abba4](https://github.com/wardensfx/OuyouyouTube/commit/06abba432032cec893d964bbfea6e2b16ff2af5e))


### Bug Fixes 🐛

* **ci:** build multi-arch (amd64/arm64) images for GHCR publish ([304fc1f](https://github.com/wardensfx/OuyouyouTube/commit/304fc1f8262c4d36872423b872ea64a20e3562d3))
* **front:** actually reload the PWA when a new version is deployed ([5a0a90b](https://github.com/wardensfx/OuyouyouTube/commit/5a0a90bb94e7b4ff3d17aec5cde542fce05578c5))
* **front:** don't wipe the persisted playlist order on an empty sync() ([065a474](https://github.com/wardensfx/OuyouyouTube/commit/065a47405258ba55180f318e734739486076db19))
* **front:** respect the iPhone safe area at the top of the app ([468a2b2](https://github.com/wardensfx/OuyouyouTube/commit/468a2b2bc5b3c846637936c37fd2bab565a30cd8))

## [0.3.0](https://github.com/wardensfx/OuyouyouTube/compare/v0.2.1...v0.3.0) (2026-07-04)


### New Features 🎉

* **ci:** automate releases with release-please + publish container images ([61b958f](https://github.com/wardensfx/OuyouyouTube/commit/61b958f90db77533f97da561cca85c2b136f88ef))
* **deploy:** point docker-compose/Quadlets at the published GHCR images ([e8fef52](https://github.com/wardensfx/OuyouyouTube/commit/e8fef52ed4a89d3fd5763afddcd8dea43bd306f8))
* **front:** add a watch history page (local IndexedDB fallback) ([80d1409](https://github.com/wardensfx/OuyouyouTube/commit/80d140961fc87604d907e2b5346e352b86e51e4e))
* **front:** add Like / Add-to-playlist buttons under the player ([d62b554](https://github.com/wardensfx/OuyouyouTube/commit/d62b5546b19b87f9d6d0fd43a54968f1855c2e80))
* **front:** drop the Like button from VideoCard listings by default ([e11068b](https://github.com/wardensfx/OuyouyouTube/commit/e11068b5d9468ec364d34f198f7c5a3f126e3825))
* **front:** hide watched videos from Subscriptions and Trending ([fa1aabc](https://github.com/wardensfx/OuyouyouTube/commit/fa1aabc305b32e33d997fe932757f3f5267fdc5e))
* **front:** persist playlist order in IndexedDB instead of localStorage ([ce4eb73](https://github.com/wardensfx/OuyouyouTube/commit/ce4eb73270a24f1d87c86f24385ed711f22126bc))
* **front:** show app version at the bottom of the sidebar ([50c66e0](https://github.com/wardensfx/OuyouyouTube/commit/50c66e0195f51161a7ca53a9e88f40ec26a4f169))
* **server:** replace flat 90% watched threshold with a duration-aware one ([86e63b5](https://github.com/wardensfx/OuyouyouTube/commit/86e63b59f3fe052d4ef39acac084b37debbe25eb))


### Bug Fixes 🐛

* address findings from the multi-agent review pass ([8efcf8a](https://github.com/wardensfx/OuyouyouTube/commit/8efcf8a7acf51f427e29426778287cd947d68381))
* **ci:** don't push :latest for prerelease GHCR images ([2d2a430](https://github.com/wardensfx/OuyouyouTube/commit/2d2a430d537c47921fedba0e2048fb2b32f4877d))


### Documentation 📝

* add screenshots and note the self-hosted-playback side benefits ([756ff8e](https://github.com/wardensfx/OuyouyouTube/commit/756ff8ea386a3fa70e563e77bd90d367b6050ccf))
