cp hifiberry-default.xml hifiberry-default-4ca.xml
cp hifiberry-default.xml hifiberry-default-dac.xml
cp hifiberry-96k.xml hifiberry-96k-dac.xml

dsptoolkit store-settings params-4ca.txt hifiberry-default-4ca.xml
dsptoolkit store-settings params-dac.txt hifiberry-default-dac.xml
dsptoolkit store-settings params-dac.txt hifiberry-96k-dac.xml

sed -i 's/Universal/Universal Beocreate/' hifiberry-default-4ca.xml
sed -i 's/Universal/Universal DSP/' hifiberry-default-dac.xml
sed -i 's/96k/DAC+ DSP 96k/' hifiberry-96k-dac.xml

