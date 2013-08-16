I'm trying to get the Plugin working again with lovefilm.de. **I'll probably break lovefilm.com support**.

## Notes
- Authorization probably doesn't work yet. Lovefilm.de is using authentication through Amazon(.de) now.
- Seasons are displayed again
- Episodes are displayed now
  - Plex can't find a Service for "http://www.lovefilm.de/tv/" URLs, but has no problems with MovieObjects and "http://www.lovefilm.de/film/" URLs
  - replacing /tv/ with /film/ fixes this, I have no clue why but it works