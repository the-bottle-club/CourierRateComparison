# Hosting the Courier Rate Comparison Tool on Digital Ocean

## What you'll end up with

- The tool live at `http://YOUR-SERVER-IP`
- Push a change to GitHub → live on the server within 5 minutes, automatically
- No SSH needed when updating rates, ever again

---

## Before you start

You'll need:
- Your server's IP address (find it in the Digital Ocean dashboard)
- Your GitHub repo URL (e.g. `https://github.com/your-username/your-repo`)
- SSH access to the server (usually `ssh root@YOUR-IP`)

---

## Step 1 — Connect to your server

Open Terminal (Mac) or Command Prompt (Windows) and run:

```
ssh root@YOUR-SERVER-IP
```

Replace `YOUR-SERVER-IP` with your actual server IP from Digital Ocean.

---

## Step 2 — Install the required software

Run these two commands one at a time:

```bash
apt update
```

```bash
apt install -y nginx git python3
```

This installs the web server (nginx), git, and Python. Just say yes to anything it asks.

---

## Step 3 — Clone your GitHub repo onto the server

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO /var/www/courier-comparison
```

Replace `YOUR-USERNAME/YOUR-REPO` with your actual GitHub repo path.

> **Private repo?** If your repo is private, GitHub will ask for your username and a Personal Access Token (not your password). Generate one at GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic). Give it `repo` read access.

---

## Step 4 — Rename the HTML file to index.html

```bash
mv "/var/www/courier-comparison/Courier Rate Comparison.html" /var/www/courier-comparison/index.html
```

This lets the browser load it automatically when someone visits the IP address.

> **Important:** Also rename the file in your GitHub repo (just rename it on GitHub or locally and push), otherwise the auto-sync in Step 7 will bring the old name back.

---

## Step 5 — Set up the web server (nginx)

Create the config file:

```bash
nano /etc/nginx/sites-available/courier
```

Paste in the following exactly (Ctrl+Shift+V to paste in most terminals):

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/courier-comparison;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Save and exit: press `Ctrl+X`, then `Y`, then `Enter`.

Now activate it:

```bash
ln -s /etc/nginx/sites-available/courier /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

At this point, you should be able to open `http://YOUR-SERVER-IP` in a browser and see the tool.

---

## Step 6 — Create the auto-sync script

This script will pull the latest changes from GitHub and regenerate the rate data file automatically.

```bash
nano /var/www/courier-comparison/sync.sh
```

Paste in:

```bash
#!/bin/bash
cd /var/www/courier-comparison
git pull origin main
python3 sync_rates.py
```

Save and exit (`Ctrl+X`, `Y`, `Enter`), then make it executable:

```bash
chmod +x /var/www/courier-comparison/sync.sh
```

Test it works:

```bash
/var/www/courier-comparison/sync.sh
```

You should see output saying it pulled from GitHub and synced the rates.

---

## Step 7 — Set up the automatic timer (cron job)

This runs the sync script every 5 minutes so changes you push to GitHub appear live automatically.

```bash
crontab -e
```

If it asks which editor to use, type `1` and press Enter (for nano).

Scroll to the very bottom and add this line:

```
*/5 * * * * /var/www/courier-comparison/sync.sh >> /var/log/courier-sync.log 2>&1
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

To confirm it's saved:

```bash
crontab -l
```

You should see the line you just added.

---

## How it all works day-to-day

1. Edit a rate file (e.g. `rates/evri.md`) in GitHub directly, or push a change from your computer
2. Within 5 minutes the server pulls the change and runs `sync_rates.py` to update the live data
3. Anyone refreshing the page will see the new rates

---

## Checking if it's working / troubleshooting

See recent sync activity:
```bash
tail -f /var/log/courier-sync.log
```

Force a manual sync right now:
```bash
/var/www/courier-comparison/sync.sh
```

Restart the web server if the page isn't loading:
```bash
systemctl restart nginx
```

Check nginx error logs:
```bash
tail -f /var/log/nginx/error.log
```

---

## Optional — Add basic password protection

If you don't want the tool publicly accessible to anyone who finds the IP:

```bash
apt install -y apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin
```

It will ask you to set a password. Then edit the nginx config:

```bash
nano /etc/nginx/sites-available/courier
```

Add these two lines inside the `location /` block:

```nginx
auth_basic "Bottle Club Internal";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Then reload nginx:

```bash
systemctl reload nginx
```

Anyone visiting will now need to enter the username (`admin`) and password you set.
