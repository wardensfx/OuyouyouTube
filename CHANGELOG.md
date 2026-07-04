# Changelog

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
