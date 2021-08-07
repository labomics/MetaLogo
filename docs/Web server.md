# MetaLogo WebServer

MetaLogo provides a public webserver for users. Users can also deploy their own MetaLogo server in their local network. In this tutorial, we will explain how to use MetaLogo webserver without coding.

First you need to visit http://metalogo.omicsnet.org (could be http://localhost:8050 if you deploy MetaLogo in your own compute), then you will see the following page if nothing goes wrong.

![server_top](../pngs/server_top.PNG)

Just as the top menu indciated, you could visit the tutorial, python packages, Journal paper, our Lab website and email us from the top menu.

There are in total six panel in the rest of MetaLogo website. The first one is a About panel which describes MetaLogo briefly. The second panel is a Input panel. You could input your data in this panel.

![input_panel](../pngs/input_panel.PNG)

For **Input Format**, you could choose from *Fasta* and *Fastq* formats. For **Sequence Type**, you could choose from *Auto*, *DNA*, *RNA* or *protein*. The term *Auto* means MetaLogo will automatically detect the sequence type. Note that if you choose the right sequence type, you need to make sure that your input sequences only involve in valid bases.  

For **Grouping By**, you could choose from *Length* and *Seq identifier*, which specify the grouping strategy in your multiple sequence logos. If you choose *Length*, MetaLogo will group sequences you input according to their lengths; if you choose *Seq identifier*, MetaLogo will identify the group information of each sequence by checking their sequence name to find a patter like **group@number-name**. Below is a valid example:

>seq1 group@1-firstgroup
ATACAGACAGAGACACAG
>seq1 group@2-secondgroup
ATACAGACAGAGACACAG

Note that in each group, sequence lengths should be the same.

**Minimum Length** and **Maximum Length** specify which sequences with certain lengths to be included for making sequence logo.