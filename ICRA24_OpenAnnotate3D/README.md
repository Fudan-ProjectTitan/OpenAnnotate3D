# ICRA24_OpenAnnotate3D

## Overview
Our program consists of `server` and `client`:
1. The client is based on `VTK` and `Python 3.8.10`, written in `C#` code.
2. The server is written in `Python` code.
3. Since our client implementation is relatively complex and requires a lot of configuration during construction, for the convenience of readers, we provide compiled executable files, which are located in the `Client` directory.
4. Since the `VTK` version used by the client is a trial version, the trial period is one month, so the downloaded client can only be used for 30 days. In this project, we will update it regularly. If you want a permanent version, please Contact the author of this article.
5. The open version of the client currently only supports reading a maximum of 10 pictures and point cloud files, and will be ignored if it exceeds the limit. If you need to support reading more files, please contact the author of this article.

## Server

### Machine configuration

- Operating system `Ubuntu 18.04` and above
- Graphics card recommended `RTX 3060` and above

### Environmental preparation

1. Before compiling the code, please go to the [OpenAI](https://openai.com/) website to apply for a `GPT Key`. We recommend using GPT 4.0.
2. After the application is completed, you need to add the following environment variables to the file `~/.bashrc`:

```bash
# Please replace sk-xxx with your application API KEY
export OPENAI_API_KEY="sk-xxx"
``` 

3. Create a new terminal and enter the following command to create the server running environment.

```bash
# Download code
mkdir openannotate3d
cd openannotate3d
git clone https://github.com/Fudan-ProjectTitan/OpenAnnotate3D.git
cd OpenAnnotate3D/ICRA24_OpenAnnotate3D/Server

conda create -n openannotate3d-icra24 python=3.8
conda activate openannotate3d-icra24
conda install pytorch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 pytorch-cuda=11.8 -c pytorch -c nvidia

pip install -r requirements.txt
```

4. Download [GroundingDINO Model Checkpoints](https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth) and [Segment Anything Model Checkpoints](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth), And put the downloaded file into the `models` folder
5. Run the code `python server.py` in the terminal
6. After completing the above steps, you will see the following output in the terminal.

![01.png](Server/assets/01.png)

The port used by the server is `5001` by default. If you need to use other ports, please modify the `port` parameter value in the following code in the `server.py` file

```python
process = multiprocessing.Process(target=(app.run(host='0.0.0.0', port=5001)))
```

After the modification is completed, you need to re-run the `server.py` file to take effect.

## Client

### Machine configuration

- Operating system `Windows 10` and above
- Memory `8G` and above
- It is recommended to use our program on machines with independent graphics, so the effect will be better

### Data preparation

1. Please put the image and point cloud files in the `Data` directory of the client. The directory structure is as follows
- Data
   - 000000.bin
   - 000000.png
   - 000001.bin
   - 000001.png
   - ...
2. The point cloud file suffix is: `.bin`, the image file suffix is: `.png`

### Equipment before use

1. Install `Python 3.8.10`, download address: [click here](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe), please note that only This version of Python can be installed. Installing other versions of Python may cause the client to fail to run properly.
2. After the installation is complete, open the terminal and enter the command `python -V`. If `Python 3.8.10` is output, the installation is successful.
3. Enter the following command to install the Python packages required for runtime. After the installation is complete, close the terminal.
```bash
pip install numpy
pip install matplotlib
```

4. Please decompress the client compressed file to an English path.
5. Find the file `OpenAnnotate3D.dll.config` under the client root directory, open it with Notepad, and modify the following configuration of the file
- `Server request address`.
- Please change the `Python environment address` to the directory selected during installation in step 1.
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
	<appSettings>
		<!-- Server request address, the value in value, please modify it according to the server's configuration address and port. -->
		<add key="Host" value="http://127.0.0.1:5001"/>

		<!-- Python environment address, please modify it according to your Python installation location -->
		<add key="PythonDLL" value="E:\Program Files\Python38\python38.dll"/>
	</appSettings>
</configuration>
```
5. Run `OpenAnnotate3D.exe`

## Citation

```bibtex
@article{zhou2023openannotate3d,
  title={OpenAnnotate3D: Open-Vocabulary Auto-Labeling System for Multi-modal 3D Data},
  author={Zhou, Yijie and Cai, Likun and Cheng, Xianhui and Gan, Zhongxue and Xue, Xiangyang and Ding, Wenchao},
  journal={arXiv preprint arXiv:2310.13398},
  year={2023}
}
```