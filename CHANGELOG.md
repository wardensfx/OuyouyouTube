# Changelog

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
