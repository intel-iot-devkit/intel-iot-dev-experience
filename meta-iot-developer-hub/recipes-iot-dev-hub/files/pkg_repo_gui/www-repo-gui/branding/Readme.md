# You can customize OEM logo file and EULA files via branding/config.xml.

## For OEM logo file:
    You have 2 ways to specify the OEM log file.
    1. The legacy way: You can add OEM logo file (named as oem-branding.png) into this folder (branding/) to enable OEM branding on Developer Hub. An example of such file is branding/oem-branding-donot-use.png.
    2. The new way: The steps are:
      1. Edit branding/config.xml, and specify your OEM logo file name (XXXX.png) without path as the content of <logo-file> element.
      2. Put your OEM logo file to branding/logos folder. An example of such file is branding/logos/logo-donot-use.png.

    The OEM logo image file format:
        Image type: PNG (high resolution)
        Image background: Transparent
        Image width: Up to 430px
        Image height: 100px

## For EULA files:
    You can multiple EULA files (as needed) so that users need to accept all of them.
    Steps:
    1. Edit branding/config.xml, and specify your EULA file name (XXXX.html) without path as the content of <html-file> element. You can add multiple <html-file> elements.
       Example:
        <custom-eulas>
            <html-file>Intel_Eula.html</html-file>
            <html-file>Eula1.html</html-file>
            <html-file>Eula2.html</html-file>
        </custom-eulas>
    2. Put all your EULA files (specified in branding/config.xml) to branding/eulas folder.

    To author an EULA html file, take branding/eulas/Intel_Eula.html as an example.

