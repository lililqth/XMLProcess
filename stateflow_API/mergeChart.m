rt = sfroot;
m = rt.find('-isa','Simulink.BlockDiagram','Name', 'Model');
fprintf('模型名称: %s\n', m.get('Name'));
chList = m.find('-isa','Stateflow.Chart');

%% 为Chart添加顶层模块
for i = 1:1:length(chList)
    minX = 99999;
    minY = 99999;
    maxX = 0;
    maxY = 0;
    stateArray = chList(i).find('-isa', 'Stateflow.State','-depth', 1);
    for j = 1:1:length(stateArray)
        position = stateArray(j).get('position');
        if position(1) < minX
            minX = position(1);
        end
        if position(2) < minY
            minY = position(2);
        end
        if position(1)+position(3) > maxX
            maxX = position(1)+position(3);
        end
        if position(2)+position(4) > maxY
            maxY = position(2)+position(4);
        end
    end
    top = Stateflow.State(chList(i));
    top.position = [minX-50 minY-50 maxX-minX+100 maxY-minY+100];
    top.name = chList(i).name;
end

%% 找到总的输入输出变量，并将其他的降级
cb = sfclipboard;
for i = 1:1:length(chList)
   top = chList(i).find('-isa', 'Stateflow.State', '-depth',1);
   data = chList(i).find('-isa', 'Stateflow.Data');
   for j = 1:1:length(data);
       des = data(j).get('Description');
       if strcmp(des, 'in')==0 &&  strcmp(des, 'out')==0
           cb.copy(data(j));
           data(j).delete;
           cb.pasteTo(top);
       end
   end
end

%% 移动chart中的顶层模块和输入输出
maxWei = chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(1) + ...
chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(3) + 50;
modelHei = chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(2);
cb = sfclipboard;
for i = 2:1:length(chList)
    % 移动顶层模块
    stateTop = chList(i).find('-isa', 'Stateflow.State','-depth', 1); % 打包
    prevGrouping = stateTop.IsGrouped;
    if (prevGrouping == 0)
        stateTop.IsGrouped = 1;
    end
    cb.copy(stateTop);
    cb.pasteTo(chList(1));
    stateTopAfter = chList(1).find('Name',stateTop.Name, ...
    '-isa','Stateflow.State');
    stateTopAfter.Position(1) = maxWei+50;
    stateTopAfter.Position(2) = modelHei;
    maxWei =  stateTopAfter.Position(1)+ stateTopAfter.Position(3) + 50;
    % 移动输入输出
    dataIO = chList(i).find('-isa', 'Stateflow.Data', '-depth', 1);
    cb.copy(dataIO);
    cb.pasteTo(chList(1));
end
%% 

sfsave('Model', 'newModel');
