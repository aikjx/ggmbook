[OPEN] GitHub Pages deploy debugging session

Session ID: github-pages-deploy

Symptoms
- GitHub Pages deployments show three failed runs.
- Public URL returns 404.

Current evidence
- Historical GitHub Actions run `#3` failed in deploy step with:
  - `Uploaded artifact size ... exceeds the allowed size of 1 GB`
  - `Failed to create deployment (status: 404) ... Ensure GitHub Pages has been enabled`
- Local remediation already completed:
  - site images compressed
  - local build passes
  - local `docs/.vitepress/dist` size is about 387.53 MB
- Local git state:
  - local `HEAD`: `988b2b0`
  - `gitcode/main`: `988b2b0`
  - `origin/main`: `4d2f435`

Hypotheses
1. The GitHub deployment page shown by the user is stale and only reflects runs before commit `988b2b0`.
2. GitHub `origin/main` has not received the fix commit, so Actions cannot run the corrected build.
3. GitHub Pages may still not be enabled with `Source = GitHub Actions`, which would keep deploy step returning 404 even after the artifact size issue is fixed.
4. Custom domain may still be set to `aikjx.com` instead of `ggmbook.aikjx.com`, causing post-deploy routing to the wrong URL.

Next checks
- Confirm whether GitHub has commit `988b2b0`.
- If not, push `main` to `origin`.
- After push, inspect the next workflow run result.
- If deploy still fails, verify Pages settings and custom domain value.
