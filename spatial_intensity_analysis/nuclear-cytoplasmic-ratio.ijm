run("Close All");
inputDir = "U:/VAMP/....../";
list = getFileList(inputDir);
for (image = 0; image < list.length; image++){
    run("Bio-Formats Windowless Importer", "open="+inputDir+list[image]);
    title = getTitle();
    print(title);
    selectWindow(title);
    idx=indexOf(title, ".tif");
    sub = title.substring(0,idx);
    addtitle = sub + "-1.tif"; 
    run("Split Channels");
    selectImage("C2-" + title);
    run("Duplicate...", " ");
    selectImage("C2-" + title);
    run("Median...", "radius=4");
    run("Gaussian Blur...", "sigma=4");
    setMinAndMax(0, 300);
    setAutoThreshold("Mean dark 16-bit no-reset");
    setOption("BlackBackground", true);
    run("Convert to Mask");
    //dilate 1 pixel to include faint DAPI edge
    run("Dilate");
    run("Create Selection");
    //Measure MET-2 Channel
    selectImage("C1-" + title);
    run("Restore Selection");
    run("Measure");
    selectImage("C2-" + title);
    run("Make Inverse");
    selectImage("C1-" + title);
    run("Restore Selection");
    run("Measure");
    run("Close All");}
selectWindow("Log");
saveAs("Text", inputDir+"ImgList.txt")
selectWindow("Results");
saveAs("Results",inputDir+"Results.csv");
