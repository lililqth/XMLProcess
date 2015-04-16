rt = sfroot;
modelName = 'all_in_one';
m = rt.find('-isa','Simulink.BlockDiagram','Name', modelName);
fprintf('ģ������: %s\n', m.get('Name'));
chList = m.find('-isa','Stateflow.Chart');

%% ΪChart��Ӷ���ģ��
for i = 1:1:length(chList)
    minX = 99999;
    minY = 99999;
    maxX = 0;
    maxY = 0;
    % set decomposition of the stateflow to be Parallel
    chList(i).set('Decomposition', 'Parallel');
    % state��Graphical function , matlab function object
    EMFunctionArray= chList(i).find('-isa', 'Stateflow.EMFunction');
    stateArray= chList(i).find('-isa', 'Stateflow.State');
    FunctionArray = chList(i).find('-isa', 'Stateflow.Function');
    objArray = [stateArray; EMFunctionArray; FunctionArray];
    % ����state�е����ж��󣬻�ȡ���ϽǺ����½�
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

%% �ҵ���������������������������Ľ���
% ������IO���м�IO
% cb = sfclipboard;
% for i = 1:1:length(chList)
%    top = chList(i).find('-isa', 'Stateflow.State', '-depth',1);
%    data = chList(i).find('-isa', 'Stateflow.Data');
%    for j = 1:1:length(data);
%        scope = data(j).get('Scope');
%        if strcmp(scope, 'Input') &&  strcmp(scope, 'Output')
%            cb.copy(data(j));
%            data(j).delete;
%            cb.pasteTo(top);
%        end
%    end
% end

% %% �ƶ�chart�еĶ���ģ����������
% maxWei = chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(1) + ...
% chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(3) + 50;
% modelHei = chList(1).find('-isa', 'Stateflow.State', '-depth', 1).Position(2);
% cb = sfclipboard;
% for i = 2:1:length(chList)
%     % �ƶ�����ģ��
%     stateTop = chList(i).find('-isa', 'Stateflow.State','-depth', 1); % ���
%     prevGrouping = stateTop.IsGrouped;
%     if (prevGrouping == 0)
%         stateTop.IsGrouped = 1;
%     end
%     cb.copy(stateTop);
%     cb.pasteTo(chList(1));
%     stateTopAfter = chList(1).find('Name',stateTop.Name, ...
%     '-isa','Stateflow.State');
%     stateTopAfter.Position(1) = maxWei+50;
%     stateTopAfter.Position(2) = modelHei;
%     maxWei =  stateTopAfter.Position(1)+ stateTopAfter.Position(3) + 50;
%     % �ƶ��������,ֻ�����Ϊ����������ı�����Ϊ����
%     dataIO = chList(i).find('-isa', 'Stateflow.Data', '-depth', 1);
%     dataExistName = chList(1).find('-isa', 'Stateflow.Data', '-depth', 1).get('Name');
%     for j = 1:1:length(dataIO)
%         if (strcmp(dataIO(j).get('Description'), 'in') || strcmp(dataIO(j).get('Description'), 'out')) && ismember(dataIO(j).get('Name'), dataExistName)==0
%             cb.copy(dataIO(j));
%             cb.pasteTo(chList(1));
%         end
%     end
% end
%% 
 sfsave(modelName, 'newModel');
