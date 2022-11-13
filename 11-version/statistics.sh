#!/bin/sh

revoke_num_total=`cat /your_path/chimera_identity.log | grep "revoke_token" | wc -l`;
 
send_tokens_total=`cat /your_path/chimera_identity.log | grep "Access token send to" | wc -l`;

wrong_tokens_total=`cat /your_path/chimera_identity.log | grep "wrong Telegram" | wc -l`;

multiple_tokens_total=`cat /your_path/chimera_identity.log | grep "Multiple token requests" | wc -l`;

invalid_number_total=`cat /your_path/chimera_identity.log | grep "Invalid number" | wc -l`;


revoke_num=`python3 -c "x=open('temp.txt','r').read();x=$revoke_num_total - int(x.split(',')[0]);print(x);"`;
send_tokens=`python3 -c "x=open('temp.txt','r').read();x=$send_tokens_total - int(x.split(',')[1]);print(x);"`;
wrong_tokens=`python3 -c "x=open('temp.txt','r').read();x=$wrong_tokens_total - int(x.split(',')[2]);print(x);"`;
multiple_tokens=`python3 -c "x=open('temp.txt','r').read();x=$multiple_tokens_total - int(x.split(',')[3]);print(x);"`;
invalid_number=`python3 -c "x=open('temp.txt','r').read();x=$invalid_tokens_total - int(x.split(',')[4]);print(x);"`;

echo "# TYPE revoke_num_total gauge" > chimera.prom;
echo "revoke_num_total $revoke_num_total" >> chimera.prom;
echo "# TYPE send_tokens_total gauge" >> chimera.prom;
echo "send_tokens_total $send_tokens_total" >> chimera.prom;
echo "# TYPE wrong_tokens_total gauge" >> chimera.prom;
echo "wrong_tokens_total $wrong_tokens_total" >> chimera.prom;
echo "# TYPE multiple_tokens_total gauge" >> chimera.prom;
echo "multiple_tokens_total $multiple_tokens_total" >> chimera.prom;
echo "# TYPE invalid_number_total gauge" >> chimera.prom;
echo "invalid_number_total $invalid_number_total" >> chimera.prom;
echo "# TYPE revoke_num gauge" >> chimera.prom;
echo "revoke_num $revoke_num" >> chimera.prom;
echo "# TYPE send_tokens gauge" >> chimera.prom;
echo "send_tokens $send_tokens" >> chimera.prom;
echo "# TYPE wrong_tokens gauge" >> chimera.prom;
echo "wrong_tokens $wrong_tokens" >> chimera.prom;
echo "# TYPE multiple_tokens gauge" >> chimera.prom;
echo "multiple_tokens $multiple_tokens" >> chimera.prom;
echo "# TYPE invalid_number gauge" >> chimera.prom;
echo "invalid_number $invalid_number" >> chimera.prom;

echo $revoke_num_total","$send_tokens_total","$wrong_tokens_total","$multiple_tokens_total","$invalid_number_total > temp.txt;
