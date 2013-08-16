I've restored basic playback functionality for lovefilm.de.
**Not tested with lovefilm.com. I've probably broken lovefilm.com support**.

## Notes
- **Autthentication** for lovefilm.de is handeled through Amazon.de now. You have to setup your Amazon.de login and change your lovefilm.de account to your Amazon account.
- Fullscreen/HD support is not perfect. You may get a message from Silverlight (where the best option seems to be "No"). And you have to manually get the focus of the window back by clicking once.
- Quirky fixes:
  - Plex can't find a Service for "http://www.lovefilm.de/tv/" URLs, but has no problems with MovieObjects and "http://www.lovefilm.de/film/" URLs
  - replacing /tv/ with /film/ fixes this, I have no clue why but it works

## TODO
- Support for movies with trailers
- Slider
- Volume
- Number of episodes missing
- Support for lovefilm.com 
  - New settings in lovefilm-de.xml could work for lovefilm.com too, but I can't test it.
- General cleanup