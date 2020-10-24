dir=$1

local_dir=`dirname $0`
uname="lmcclymont"
remote_loc="lmcclymont-hadoop-01.fab4.prod.booking.com"
remote_dir="/home/lmcclymont/public/lmcclymont/git_laurie/"

cd ${local_dir}/
echo `pwd`
mkdir -p ${local_dir}/${dir}
umount -f ${local_dir}/${dir}
echo "sshfs -o auto_cache ${uname}@${remote_loc}:${remote_dir}/${dir} ${dir}"
sshfs -o auto_cache ${uname}@${remote_loc}:${remote_dir}/${dir} ${local_dir}/${dir}
