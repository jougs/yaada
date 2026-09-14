# yaada
Yet Another AppDaemon App (repository)

## Deployment
On a fresh installation of Home Assistant Operating System, run

```bash
basedir=/share/appdaemon
haconf=/homeassistant/configuration.yaml
mkdir -p ${basedir}/hass_entities/input_boolean
git clone -b m4 https://github.com/jougs/yaada.git ${basedir}/yadaa
ln -s ${basedir}/yadaa/conf/appdaemon.conf /addon_configs/a0d7b954_appdaemon/
echo -e '\ninput_boolean: !include_dir_merge_named '${basedir}'/hass_entities/input_boolean' >> ${haconf}
```

## Secrets

The structure of the `/addon_configs/a0d7b954_appdaemon/secrets.yaml`
file is the following:

```yaml
latitude:
longitude:
elevation:

telegram_target:

hargassner_ip:

mqtt_host: 
mqtt_user:
mqtt_password:

# https://developer.spotify.com/dashboard/
spotify_client_id:
spotify_client_secret:
```
