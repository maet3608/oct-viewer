# oct-viewer

A simple viewer for Optical Coherence Tomography (OCT) volumes.

![UI](https://github.com/maet3608/oct-viewer/blob/master/ui.png)


## Usage

```
python oct_viewer.py <datadir>
```


## Data

The data folder must contain OCT volumes as 3D numpy arrays (``dtype='uint8'``), 
where the first axis is the B-scan, followed by rows(depth) and cols(width) 
of the B-scan, with image origin in the upper left corner.

