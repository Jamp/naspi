#!/bin/bash

HOSTNAME=naspi
LOCAL_TIMEZONE=America/Lima
PERSONAL_USER=jamp
CAMS_USER=cams
CAMS_PASSWD=`openssl rand -base64 12`
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`

NAS_DIRECTORY=/NAS

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
mkdir $NAS_DIRECTORY

sed -i s/'#inotify=yes'/'inotify=yes'/g /etc/minidlna.conf
sed -i s/'media_dir='/'#media_dir='/g /etc/minidlna.conf
tee -a /etc/minidlna.conf <<EOF
media_dir=V,/NAS/Películas
media_dir=V,/NAS/Series
EOF

# Dejar preparado para montar el disco del NAS
# para obtenerlo `blkid /dev/<NAS_DISK>`
echo "# PARTUUID=<UUID_NAS_DISK> /NAS	ext4	defaults,errors=remount-ro	0	1" >> /etc/fstab

# Dejar preparado para compartir por NFS
echo "# /NAS <my_ip>(rw,sync,no_subtree_check,no_root_squash)  # My computer" >> /etc/exports
echo "# /NAS/Películas <my_network>/16(rw,sync,no_subtree_check,no_root_squash)  # My network" >> /etc/exports
echo "# /NAS/Series <my_network>/16(rw,sync,no_subtree_check,no_root_squash)  # My network" >> /etc/exports
echo "# /NAS/Public <my_network>/16(rw,sync,no_subtree_check,no_root_squash)  # My network" >> /etc/exports

# Crear usuario para las cámaras y poder almacenar
# un copia de los videos de vigilancia
useradd -r -s /bin/false $CAMS_USER
( echo $CAMS_PASSWD; echo $CAMS_PASSWD ) | smbpasswd -a $CAMS_USER

tee -a /etc/samba/smb.conf <<EOF
[Public]
path = /NAS/Public
writeable=Yes
create mask=0777
directory mask=0777
public=yes

[Series]
path = /NAS/Series
writeable=Yes
create mask=0777
directory mask=0777
public=yes

[Películas]
path = /NAS/Películas
writeable=Yes
create mask=0777
directory mask=0777
public=yes

[CAMS]
path = /NAS/CAMS
writeable=Yes
create mask=0777
directory mask=0777
public=no
valid user=$PERSONAL_USER $CAMS_USER
EOF

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

echo $CAMS_PASSWD > cams_passwd.txt

reboot
