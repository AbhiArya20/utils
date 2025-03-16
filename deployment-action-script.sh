    #!/bin/bash
    WEBSITE="abhiarya.in"
    GITHUB_URL="https://github.com/AbhiArya20/jainsonsindia"
    GITHUB_HASH=your_github_action_hash
    GITHUB_TOKEN=your_github_action_token

    sudo apt install certbot python3-certbot-nginx -y

    sudo touch "/etc/nginx/sites-available/$WEBSITE"

    sudo echo "
    sudo tee "/etc/nginx/sites-available/$WEBSITE" > /dev/null <<EOF
    user nginx;
    worker_processes auto;

    error_log /var/log/nginx/error.log notice;
    pid /var/run/nginx.pid;

    events {
        worker_connections 1024;
    }

    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        map \$http_upgrade \$connection_upgrade {
            default upgrade;
            '' close;
        }

        # upstream websocket {
        #     server socket-service:3004;
        # }

        log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                        '\$status \$body_bytes_sent "\$http_referer" '
                        '"\$http_user_agent" "\$http_x_forwarded_for"';

        access_log /var/log/nginx/access.log main;

        sendfile on;
        tcp_nopush on;

        keepalive_timeout 65;

        server {
            listen 443 ssl;

            server_name $WEBSITE;

            client_max_body_size 20m;

            ssl_certificate /etc/letsencrypt/live/$WEBSITE/fullchain.pem;
            ssl_certificate_key /etc/letsencrypt/live/$WEBSITE/privkey.pem;

            location /docs/ {
                proxy_pass http://docs:3001/;
            }

            location / {
                proxy_pass http://web:3000/;
            }

            location /socket.io/ {
                proxy_pass http://socket-service:3004/socket.io/;
                proxy_http_version 1.1;
                proxy_set_header Upgrade \$http_upgrade;
                proxy_set_header Connection "upgrade";
            }

            location /.well-known/acme-challenge/ {
                root /var/www/certbot;
            }
        }

        include /etc/nginx/conf.d/*.conf;
    }
    EOF"

    sudo systemctl reload nginx

    sudo ufw allow 'Nginx Full'
    sudo ufw allow openSSH



    sudo certbot --nginx -d "$WEBSITE" "www.$WEBSITE" "portfolio.$WEBSITE"


    mkdir actions-runner && cd actions-runner
    curl -o actions-runner-linux-x64-2.320.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-linux-x64-2.320.0.tar.gz
    echo "$GITHUB_HASH actions-runner-linux-x64-2.320.0.tar.gz" | shasum -a 256 -c
    tar xzf ./actions-runner-linux-x64-2.320.0.tar.gz

    ./config.sh --url $GITHUB_URL --token $GITHUB_TOKEN

    sudo ./svc.sh install
    sudo ./svc.sh start

# sudo touch setup.sh && sudo chmod +777 ./setup.sh && sudo vim ./setup.sh
