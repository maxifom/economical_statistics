mkdir ./data;
export fileid=1nHPn4WsJ8KGPTgSmwNMY7Ud6VUgcjC6_;
export filename=1.tar;
wget -nv --save-cookies cookies.txt 'https://docs.google.com/uc?export=download&id='$fileid -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' > confirm.txt;
wget -nv --load-cookies cookies.txt -O $filename 'https://docs.google.com/uc?export=download&id='$fileid'&confirm='$(<confirm.txt);
rm -f confirm.txt cookies.txt;
tar -xf 1.tar -C ./data;
rm -r 1.tar;