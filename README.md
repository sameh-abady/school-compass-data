# school-compass-data

Live data for the family School Compass site. **Everything here is encrypted.**

- `payload.json` — page, AES-GCM, key derived from the family password (PBKDF2).
- `feed.enc`, `cal.enc` — AES-GCM with a random key wrapped by RSA-OAEP (`datakey.pub.pem`); signed with a key derived from the family password. Only the site's server functions can decrypt them.
- `tools/` — the scripts that produce these files (no secrets inside).
