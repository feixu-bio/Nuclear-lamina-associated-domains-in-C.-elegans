nonpha_dis = [];
pha_dis = [];
BothON_dis = [];
OneON_dis = [];
BothOFF_dis = [];

filelist = dir(['U:\Scientific Data\RG-SM01-Data01\Fei\Imaging2\20221119pha-4ATADs_FeiSubregion2\20221119DNAFISH\calcu_dis_peri\nuc_pha4_peri*.mat']);
for ii = 1:length(filelist)
    load(filelist(ii).name)
if Age>50
for i = 1:length(List_Nuc_Dot_Terri)
    % nonpha distance
    if List_Nuc_Dot_Terri(i).BelongToPha == 0
       nonpha_dis = [nonpha_dis List_Nuc_Dot_Terri(i).peri];
    % pha distance
    elseif List_Nuc_Dot_Terri(i).BelongToPha == 1
        pha_dis = [pha_dis List_Nuc_Dot_Terri(i).peri];
       if  isfield(List_Nuc_Dot_Terri,'IntronNum') 
            if isempty(List_Nuc_Dot_Terri(i).IntronNum) % 2OFF distance
               BothOFF_dis = [BothOFF_dis List_Nuc_Dot_Terri(i).peri];
            end
       end   
    end
    if  isfield(List_Nuc_Dot_Terri,'IntronNum')
        if List_Nuc_Dot_Terri(i).IntronNum >= 2 %both ON distance
           BothON_dis = [BothON_dis List_Nuc_Dot_Terri(i).peri];
        % 1ON distance
        elseif List_Nuc_Dot_Terri(i).IntronNum == 1
           OneON_dis = [OneON_dis List_Nuc_Dot_Terri(i).peri];
        end
    elseif ~isfield(List_Nuc_Dot_Terri,'IntronNum')
        BothON_dis = [];
        OneON_dis = [];
    end
end
end
end

pha = pha_dis(pha_dis<1);
nonpha = nonpha_dis(nonpha_dis<1);
ON2 = BothON_dis(BothON_dis<1);
ON1 = OneON_dis(OneON_dis<1);
ON0 = BothOFF_dis(BothOFF_dis<1);

save('combine_peri_dis_over50.mat','ON0','ON1','ON2','nonpha','pha');
