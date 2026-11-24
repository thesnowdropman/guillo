# Fantasy Scoreboard

A fantasy scoreboard website that pulls NFL player stats from [SportsDataIO](https://sportsdata.io). It scores each owner's roster with your league rules, shows how many players still have games left, and refreshes every 5 minutes through GitHub Actions and GitHub Pages. It makes no projections or predictions.

Python standard library only. No dependencies.

## Scoring

| Stat | Points |
| --- | --- |
| Reception | 1.0 |
| Yards (passing, rushing, receiving) | 0.1 per yard (10 yards = 1.0, decimals kept) |
| Touchdown (passing, rushing, receiving) | 1.0 |

Interceptions, fumbles, and kicking are not scored. Edit `fantasy_scoreboard/scoring.py` to change the rules.

## How it works

1. A GitHub Actions workflow runs every 5 minutes.
2. It calls SportsDataIO for player stats and game status, using your key stored as a repository secret.
3. It writes `site/data/scoreboard.json` and deploys the `site/` folder to GitHub Pages.
4. The page in `site/index.html` reloads the JSON every 60 seconds.

Your API key never appears in the public site. It lives only in the repository's secrets.

## Setup

### 1. Put the files in a GitHub repository

Create a new repository and upload everything in this folder, including the hidden `.github` folder.

### 2. Add your league file

Copy `data/league.example.json` to `data/league.json` and fill in your owners and starting players. Each player needs the name as SportsDataIO spells it and their NFL team abbreviation (for example `CIN`, `WAS`). The workflow reads this file, so it must be in the repository.

### 3. Add your API key as a secret

Settings → Secrets and variables → Actions → **New repository secret**
- Name: `SPORTSDATAIO_KEY`
- Value: your SportsDataIO key

### 4. Turn on GitHub Pages

Settings → Pages → Build and deployment → Source → **GitHub Actions**

### 5. Run it once

Actions tab → "Update scoreboard" → **Run workflow**. When the run finishes, the site is at `https://<your-username>.github.io/<repository-name>/`. Scheduled runs keep it current after that.

### Each week

Change `WEEK` in `.github/workflows/scoreboard.yml` (and `SEASON` when the season changes), then commit the change.

## Visibility

On GitHub's free plan, Pages isn't available for private repositories. If the repository is public, anyone with the link can see the scoreboard, including the rosters in `data/league.json`.

## Limits

- **Refresh timing:** Scheduled workflows run every 5 minutes at the fastest, and GitHub can delay them by several minutes. Updates are near-live, not instant.
- **Stat delays:** Scores are only as fresh as SportsDataIO's feed for your plan.
- **Name matching:** Players are matched by name, so two players with the same name would collide.

## Local use

```bash
export SPORTSDATAIO_KEY=your_key_here
python -m fantasy_scoreboard data/league.json --season 2026 --week 12 --watch 60
```

To generate the website data locally:

```bash
python -m fantasy_scoreboard.export --league data/league.json --season 2026 --week 12 --out site/data/scoreboard.json
```

To view the site locally, run `python -m http.server` from inside `site/` and open the printed address. Browsers often block local JSON files opened directly from disk.

## Tests

```bash
python -m unittest discover tests
```

## Before you rely on it

I haven't run this against the live API. The SportsDataIO field names (`ReceivingYards`, `AwayScore`), status values (any value starting with `F` counts as final), and endpoint paths follow SportsDataIO's v3 NFL format from memory. Check them against a real response after the first run. The Actions log will show any export error.
