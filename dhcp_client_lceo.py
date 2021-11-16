# -*- coding: utf-8 -*-
from lceo import *
import re
import sys
log_fname = "/var/lib/dhcp/dhcpWatcher/logs"  # путь к файлу логов
# в логах отображается состояние dhcpWatcher:
# 1) INITIAL DHCP's IP is [DHCP SERVER's IP address] -
#	отображает IP адрес DHCP сервера полученный при запуске dhcpWatcher
# 	из файла dhclient.leases
# 2) DHCPserver is LOST - DHCP сервер выполнил переход на другой IP
# 3) DHClient RESTARTED - DHCP клиент перезапущен
# 4) NEW DHCP IP [new IP] - новый IP адрес DHCP сервера

##########################################################################

leases_fname = "/var/lib/dhcp/dhclient.leases"  # путь к файлу данных dhcp аренды
# функция чтения IP адреса DHCP сервера из файла leases_fname


def get_dhcp_ip(f_name):
    f = open(f_name, 'r')
    leases = str(f.read())
    try:
        ip = re.findall(r'dhcp-server-identifier (.*);', leases)[-1]
    except:
        ip = "192.168.0.1"
    f.close()
    return ip


# функция записи в файл логов
def log(s):  # s - записываемая строка
    try:
        f = open(log_fname, 'a')
        t_stamp = t.strftime("%d-%m-%Y %H:%M:%S \t", t.gmtime(t.time()))
        s = t_stamp + s + "\n"  # добавляем временную метку перед записью
        f.write(s)
        f.close()
        print(s)
    except:
        print(s)


def get_veth_ip():
    cmd_result = exec_com("ifconfig eth0")[0]
    ip = re.findall(r'(\d+\.\d+\.\d+\.\d+)', cmd_result)[0]
    return ip


def get_mask():
    cmd_result = exec_com("ifconfig eth0")[0]
    mask = re.findall(r'netmask (\d+\.\d+\.\d+\.\d+)', cmd_result)[0]
    return mask


def get_random_ip(dhcp_ip, mask):
    numbers = re.findall(r'\d+', dhcp_ip)
    count = re.findall(r'255', mask).__len__()
    result = ""
    for n in range(count, numbers.__len__(), 1):
        numbers[n] = random.randint(0, 255)
        if count == n:
            break
    for number in numbers:
        result += str(number) + "."
    result = result[0: result.__len__()-1]
    return result


def gen_random_mac_address():
    result = ""
    for i in range(17):
        if ((i+1) % 3 ==0) & (i>0):
            result += ':'
        else:
            rand_number = random.randint(0, 15)
            rand_symbol = str(rand_number)
            if rand_number == 15:
                rand_symbol = 'f'
            if rand_number == 14:
                rand_symbol = 'e'
            if rand_number == 13:
                rand_symbol = 'd'
            if rand_number == 12:
                rand_symbol = 'c'
            if rand_number == 11:
                rand_symbol = 'b'
            if rand_number == 10:
                rand_symbol = 'a'
            result += rand_symbol
    return result


def make_pc_from_ip(ip):
    result = {
        "ip": ip,
        "mac": gen_random_mac_address()
    }
    return result


def make_pc_list(dhcp_ip, mask, count_pc):
    result = []
    pc_list = []
    for i in range(count_pc):
        pc_list.append(make_pc_from_ip(get_random_ip(dhcp_ip, mask)))
    plus = 0
    for ip in pc_list:
        plus+=1
        for i in range(plus, pc_list.__len__()):
            result.append((ip, pc_list[i]))
    return result


##########################################################################
# Инициализация
count_pc_lceo = int(sys.argv[1])
log("INITIALIZATION...")
log("Getting last DHCP server's IP...")
# читаем IP адрес DHCP сервера, записываем в переменную dhcp_ip_addr
dhcp_ip_address = get_dhcp_ip(leases_fname)
# записываем в лог начальный адрес DHCP сервера
log_str = "[ + ] DHCP's IP is " + dhcp_ip_address
log(log_str)
exec_com("dhclient -v eth0")
# exec_com("killall -9 dhclient")
current_ip = get_veth_ip() #в данной переменной хранится текущий ip-адрес порта, к которому закреплен dhcp
log_str = "[ + ] Ethernet interface was set. Eth0 has IP " + current_ip
dhcp_mask = get_mask()
pc_list = make_pc_list(dhcp_ip_address, dhcp_mask, count_pc_lceo)
log(log_str)
print(pc_list)
lceo = Lceo(pc_list)

# Основной цикл
while True:
    try:
        # выполняем ping DHCP сервера
        t.sleep(1)
        command = "ping " + str(dhcp_ip_address) + " -c 2"
        ping_out = exec_com(command)[0]
        # извлекаем из вывода количество принятых от сервера ICMP пакетов
        pk_received = int(re.findall(r'(\d) received', ping_out)[-1])
        if pk_received < 1:  # если не принято ни одного пакет
            log("[ !!! ] DHCPserver is LOST")
            exec_com("dhclient -v eth0") # перезапускаем DHCP клиент
            t.sleep(1)
            # exec_com("killall -9 dhclient")
            dhcp_ip_address = get_dhcp_ip(leases_fname)  # получаем новый адрес сервера
            current_ip = get_veth_ip()
            log_str = "[ + ] DHClient RESTARTED. Eth0: {0} / DHCP - {1}".format(current_ip, dhcp_ip_address)
            pc_list = make_pc_list(dhcp_ip_address,get_mask(), count_pc_lceo)
            lceo.set_pc_list(pc_list)
            log(log_str)
        t.sleep(0.5)
    except:
        # в случае ошибки ждем 5 с, повторяем цикл сначала
        exec_com("dhclient -v eth0")
        t.sleep(1)
