sz = 500;
filelist = dir(['U:\VAMP\cokiny55\calcu_dis_peri\*Reconstruction.mat']);
for ii = 1:length(filelist)
    load(filelist(ii).name)
    newStr = extractBetween(filelist(ii).name,"FOV-","-Emb-");
    for i = 1:length(NucStruct)
        dis_to_peri = [];
        for j = 1:length(Dot.x)
            tf = inShape(NucStruct(i).alphaShape,Dot.x(j),Dot.y(j),Dot.z(j));
               if tf == 1
               % reshape pha4 loci in um
               px = Dot.x(j)*0.11;
               py = (sz-Dot.y(j))*0.11;
               pz = Dot.z(j)*0.2;
               % reshape nuclear center in um
               cx = NucStruct(i).nuc_props.Centroid(1)*0.11;
               cy = (sz-NucStruct(i).nuc_props.Centroid(2))*0.11;
               cz = NucStruct(i).nuc_props.Centroid(3)*0.2;
               % nearest_surface
               I = nearestNeighbor(NucStruct(i).alphaShape,Dot.x(j),Dot.y(j),...
                   Dot.z(j));
               % reshape nearest_surface dot in um
               near_dot_x = NucStruct(i).alphaShape.Points(I,1)*0.11;
               near_dot_y = (sz-NucStruct(i).alphaShape.Points(I,2))*0.11;
               near_dot_z = (NucStruct(i).alphaShape.Points(I,3))*0.2;
               %calculate distance periphery to pha-4
               radial_dot_dis = ((px - near_dot_x).^2+ ...
                                 (py - near_dot_y).^2+ ... 
                                 (pz - near_dot_z).^2).^0.5;
               %calculate distance periphery to center
               radial_center_dis = ((cx - near_dot_x).^2+ ...
                                    (cy - near_dot_y).^2+ ... 
                                    (cz - near_dot_z).^2).^0.5;
               norm_dis = radial_dot_dis/radial_center_dis;
               dis_to_peri = [dis_to_peri norm_dis];
               end
        end
        List_Nuc_Dot_Terri(i).peri = dis_to_peri;
    end
    
%     figure
%     hold on
%     for i = 1:length(NucStruct)
%     h{1} = plot(NucStruct(i).alphaShape  ,'FaceColor','red','FaceAlpha',0.05,'LineStyle', 'none');
%     h{2} = scatter3(NucStruct(i).nuc_props.Centroid(1),...
%                     NucStruct(i).nuc_props.Centroid(2),...
%                     NucStruct(i).nuc_props.Centroid(3),'ok');
%     end
%     h{2} = scatter3(Dot.x(1,:), Dot.y(1,:), Dot.z(1,:) , '.','blue');
    List_Nuc_Dot_Terri = rmfield(List_Nuc_Dot_Terri, 'Terri');    
    Age = List_Nuc_Dot_Terri(end).BlobID;
    save(['nuc_pha4_peri_' newStr{1,1} '.mat'],'List_Nuc_Dot_Terri','Age')
end
