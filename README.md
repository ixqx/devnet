Домашнее задание первого дня DevNet 2020 <br>

Необходимо:<br>
1.Собрать со всех устройств файлы конфигураций, сохранить их на диск, используя имя устройства и текущую дату в составе имени файла.<br>
2. Проверить на всех коммутаторах-включен ли протокол CDP и есть ли упроцесса CDPна каждом из устройств данные о соседях.<br>
3. Проверить, какой типпрограммного обеспечения(NPEили PE)* используется на устройствах исобрать со всех устройств данные о версиииспользуемого ПО.<br>
4. Настроить на всех устройствах timezone GMT+0, получение данных для синхронизациивремени от источника во внутренней сети, предварительно проверив его доступность.<br>
5. Вывести отчет в виде нескольких строк, каждая изкоторых имеет следующийформат, близкий к такому:<br>
Имя устройства -тип устройства -версия ПО -NPE/PE -CDP on/off, Xpeers-NTP in sync/not sync.<br>
Пример:<br>
ms-gw-01|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |PE|CDP is ON,5peers|Clock in Sync<br>
ms-gw-02|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |NPE|CDP is ON,0 peers|Clock in Sync<br>

Данные по устройствам вносятся в devices.yaml файл в виде списка словарей:<br>
- device_type: cisco_ios<br>
  ip: 192.168.100.1<br>
  username: cisco<br>
  password: cisco<br>
  secret: cisco<br>
- device_type: cisco_ios<br>
  ip: 192.168.100.2<br>
  username: cisco<br>
  password: cisco<br>
  secret: cisco<br>
- device_type: cisco_ios<br>
  ip: 192.168.100.3<br>
  username: cisco<br>
  password: cisco<br>
  secret: cisco<br>
  <br>
  Образец вывода:<br>
R1|7200|15.2(4)M11|PE|CDP is ON, 3 peers|Clock in Sync<br>
R2|7200|15.2(4)M11|PE|CDP is ON, 3 peers|Clock not in Sync<br>
R3|7200|15.2(4)M11|PE|CDP is ON, 3 peers|Clock not in Sync<br>



