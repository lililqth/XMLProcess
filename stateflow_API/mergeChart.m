rt = sfroot;
modelName = 'all_in_one';
m = rt.find('-isa','Simulink.BlockDiagram','Name', modelName);
fprintf('模型名称: %s\n', m.get('Name'));
chList = m.find('-isa','Stateflow.Chart');

%% 为Chart添加顶层模块
for i = 1:1:length(chList)
    minX = 99999;
    minY = 99999;
    maxX = 0;
    maxY = 0;
    % set decomposition of the stateflow to be Parallel
    chList(i).set('Decomposition', 'Parallel');
    % state，Graphical function , matlab function object
    EMFunctionArray= chList(i).find('-isa', 'Stateflow.EMFunction');
    stateArray= chList(i).find('-isa', 'Stateflow.State');
    FunctionArray = chList(i).find('-isa', 'Stateflow.Function');
    objArray = [stateArray; EMFunctionArray; FunctionArray];
    % 遍历state中的所有对象，获取左上角和右下角
    for j = 1:1:length(objArray)
        position = objArray(j).get('position');
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
    top.position = [minX-100 minY-100 maxX-minX+200 maxY-minY+200];
    top.name = chList(i).name;
end

%% 改变数据层次
%添加顶层模块后，所有的数据都在顶层模块之外
%保留所有的输出变量，和总输入变量
cb = sfclipboard;
for i = 1:1:length(chList)
   top = chList(i).find('-isa', 'Stateflow.State', '-depth',1);
   data = chList(i).find('-isa', 'Stateflow.Data');
   for j = 1:1:length(data);
       scope = data(j).get('Scope');
       description = data(j).get('Description');
       if ~(strcmp(scope, 'Output') || (strcmp(scope, 'Input') && strcmp(description, 'in')))
           data(j).Scope = 'Local';
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
    
    % 移动输入输出,只将标记为总输入输出的变量置为顶层，不可重复
    dataIO = chList(i).find('-isa', 'Stateflow.Data', '-depth', 1);
    for j = 1:1:length(dataIO)
        dataExist = chList(1).find('-isa', 'Stateflow.Data', '-depth', 1);
        tmp = ismember(dataExistName, dataIO(j).get('Name'));
        if (strcmp(dataIO(j).get('Description'), 'in') || strcmp(dataIO(j).get('Description'), 'out'))
            equal = false;
            for k =1:1:length(dataExist)
                if strcmp(dataExist(k).get('Name'), dataIO(j).get('Name'))
                    equal= true;
                    break;
                end
            end
            if equal == false
                cb.copy(dataIO(j));
                cb.pasteTo(chList(1));
            end
        end
    end
end
%chList(1).set('Name',modelName);
%% 另存为
sfsave(modelName, 'newModel');
