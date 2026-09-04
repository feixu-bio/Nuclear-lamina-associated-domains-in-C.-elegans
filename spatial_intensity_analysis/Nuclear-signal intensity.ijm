run("Close All");
inputDir = "U:/VAMP/....../";
list = getFileList(inputDir);
for (image = 0; image < list.length/2; image++){
    run("Bio-Formats Windowless Importer", "open="+inputDir+list[image]);
    title = getTitle();
    selectWindow(title);
    idx=indexOf(title, ".vsi");
    sub = title.substring(0,idx);
    addtitle = sub + "-1.vsi";
    run("Split Channels");
    //process DAPI
    selectImage("C1-" + title);
    run("Median...", "sigma=4 stack");
    run("Gaussian Blur...", "sigma=4 stack");
    run("Z Project...", "projection=[Max Intensity]");
    run("Translate...", "x=2 y=2 interpolation=None");
    //process CPD
    selectImage("C2-" + title);
    run("Median...", "sigma=2 stack");
    run("Z Project...", "projection=[Max Intensity]");
    //
    selectImage("MAX_C1-" + title);
    //run("Threshold...");
    setAutoThreshold("IsoData dark no-reset");
    setOption("BlackBackground", true);
    run("Convert to Mask");
    run("Create Selection");
    selectImage("MAX_C2-" + title);
    run("Restore Selection");
    run("Measure");
    //measure the background
    selectImage("MAX_C1-" + title);    
    run("Make Inverse");
    selectImage("MAX_C2-" + title);
    run("Restore Selection");
    //measure the background
    run("Measure");    
    run("Close All");}
saveAs("Results",inputDir+"Results_CPD_intenstiy.csv");
//close the Results window
run("Close");  
