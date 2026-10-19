# Canton SI and dev studio directory

Internal directory of the SIs and dev studios the Canton Foundation works with or is
targeting: their client category, their proof of work on Canton, and whether they are
ready for institutional work.

## What's in this repo

| File | What it is |
| --- | --- |
| `index.html` | The directory. Open this. |
| `orgs/` | One JSON file per organisation. `orgs/_template.json` shows every field. |
| `build.py` | Checks the files in `orgs/` and puts their data into `index.html`. |
| `.github/workflows/directory.yml` | Runs `build.py` for you on GitHub. |

## View the directory

Click `index.html`, click **Download raw file**, and double-click the downloaded file.

## Add a new organisation

1. Open the directory and click **Add an organisation**.
2. Fill in the form and click **Continue to GitHub**, then **Open GitHub**.
3. GitHub opens with `orgs/<name>.json` already written. Click **Commit changes** and confirm.

That's it. `index.html` updates within a minute or two. If you chose to open a pull request
instead of committing directly, it is checked and merged automatically because it only adds
a new organisation. The form refuses names already in the directory, and GitHub will not let
it overwrite an existing file, so adding can never change someone else's entry.

## Change an existing organisation

Open its file in `orgs/`, click the pencil icon, edit, choose **Create a new branch and start
a pull request**, and open the pull request. It is checked automatically and the workflow asks
for a review; it is not merged automatically. `index.html` updates after it is merged.

## One-time setup

1. **Visibility**: Private, or Internal if the org belongs to a GitHub Enterprise account.
2. **Access**: give the Foundation team **Write** access.
3. **Actions**: Settings > Actions > General > Workflow permissions: choose
   **Read and write permissions**, so the workflow can update `index.html`.
4. **Repo name**: if the repo is not `canton-network-devs/si-directory`, change `GITHUB_REPO`
   near the bottom of `index.html` (search for `GITHUB_REPO`).
5. **Logo**: upload the official horizontal yellow Canton logo from the brand kit
   (canton.network/brand-kit-trademark-use) to the repo root as `canton-logo.svg`.
   It shows when people download the whole repo; the page works without it.
6. **GitHub Pages**: leave it off. A Pages site is public on the internet unless the org is on
   GitHub Enterprise Cloud and the site's visibility is set to private.

### What GitHub can and can't enforce

GitHub permissions can't tell "add a file" apart from "edit a file": anyone with Write access
can technically commit an edit straight to `main`. What you get instead:

- Adding through the form can only create new files, never change existing ones.
- Edit pull requests are never auto-merged and get a review request.
- Every change is in the commit history with the person's name, so a bad edit is easy to spot and revert.

Hard-blocking direct edits would need branch protection on `main`, which would also block the
workflow from updating `index.html`. If you ever need that, it can be done, but it adds setup.

## Running the check yourself (optional)

```
python3 build.py --check   # check the files in orgs/
python3 build.py           # check, then update index.html
```

No installs needed beyond Python 3.
