#!/bin/bash
$PERSONAL_USER=jamp
$CAMS_USER=cams
$CAMS_PASSWD=`openssl rand -base64 32`
$FONT_DIRECTORY=/usr/share/fonts/truetype
$SOURCE_LOCAL=/usr/local/src
$WORK_DIRECTORY=$SOURCE_LOCAL/naspi

# Chequear solo correr como root para evitar problemas
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root"
  exit 1
fi

# De primer chicharrón debemos quedar actualizado
apt-get update && apt-get upgrade -y
apt-get install vim git python3-pip nfs-kernel-server samba samba-common-bin minidlna -y

# Este el directorio para montar el disco en red
mkdir /NAS

# reemplazar el usuario pi por mi usuario por comodidad
usermod -l $PERSONAL_USER pi
usermod -m -d /home/$PERSONAL_USER $PERSONAL_USER

sed -i s/pi/$PERSONAL_USER/g /etc/passwd
sed -i s/pi/$PERSONAL_USER/g /etc/shadow
sed -i s/pi/$PERSONAL_USER/g /etc/group
sed -i s/pi/$PERSONAL_USER/g /etc/sudoers
sed -i s/pi/$PERSONAL_USER/g /etc/gshadow
mv /home/pi /home/$PERSONAL_USER

# Crear usuario para las cámaras y poder almacenar
# un copia de los videos de vigilancia
useradd -m -s /bin/false $CAMS_USER
smbpasswd -a $CAMS_USER -x $CAMS_PASSWD

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
