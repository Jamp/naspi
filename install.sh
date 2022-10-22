#!/bin/bash

HOSTNAME=naspi
LOCAL_TIMEZONE=America/Lima
PERSONAL_USER=jamp
CAMS_USER=cams
CAMS_PASSWD=`openssl rand -base64 12`
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`

# Básico para hacer funcionar las cosas
FONT_DIRECTORY=/usr/share/fonts/truetype
SOURCE_LOCAL=/usr/local/src
WORK_DIRECTORY=$SOURCE_LOCAL/naspi

# Chequear solo correr como root para evitar problemas
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root"
  exit 1
fi

# Cambiando el hostname
hostnamectl set-hostname $HOSTNAME
sed -i s/$CURRENT_HOSTNAME/$HOSTNAME/g /etc/hosts
timedatectl set-timezone $LOCAL_TIMEZONE

# De primer chicharrón debemos quedar actualizado
apt-get update && apt-get upgrade -y
apt-get install vim git python3-pip nfs-kernel-server samba samba-common-bin minidlna -y

# Este el directorio para montar el disco en red
mkdir /NAS

# Crear usuario para las cámaras y poder almacenar
# un copia de los videos de vigilancia
useradd -r -s /bin/false $CAMS_USER
( echo $CAMS_PASSWD; echo $CAMS_PASSWD ) | smbpasswd -a $CAMS_USER

# Poniendo a punto con la fuente que me gusta para pantalla Oled
curl https://fonts.google.com/download?family=Silkscreen -o $SOURCE_LOCAL/Silkscreen.zip
mkdir -p $FONT_DIRECTORY/Silkscreen
unzip $SOURCE_LOCAL/Silkscreen.zip -d $FONT_DIRECTORY/Silkscreen

# Descargamos el código para poder pasar
# Y poner a punto todo
git clone https://github.com/Jamp/naspi.git $WORK_DIRECTORY
pip3 install -r $WORK_DIRECTORY/nas-control/requeriments.txt

cp $WORK_DIRECTORY/nas-control.service /lib/systemd/system/nas-control.service
systemctl daemon-reload

systemctl enable --now nfs-kernel-server
systemctl enable --now smbd
systemctl enable --now nas-control

reboot
