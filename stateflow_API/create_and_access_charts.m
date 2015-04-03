sfnew;
rt = sfroot;
m = rt.find('-isa','Simulink.BlockDiagram');
ch = m.find('-isa','Stateflow.Chart');
sA = Stateflow.State(ch);
sA.Name = 'A';
sA.Position = [50 50 310 200];
sA1 = Stateflow.State(ch);
sA1.Name = 'A1';
sA1.Position = [80 120 90 60];
sA2 = Stateflow.State(ch);
sA2.Name = 'A2';
sA2.Position = [240 120 90 60];
tA1A2 = Stateflow.Transition(ch);
tA1A2.Source = sA1;
tA1A2.Destination = sA2;
tA1A2.SourceOClock = 3;  %�����ӵ�λ��
tA1A2.DestinationOClock = 9; %�ŵ��ӵ�λ��


% Add a default transition to state A
dtA = Stateflow.Transition(ch);
dtA.Destination = sA;
dtA.DestinationOClock = 0;
xsource = sA.Position(1)+sA.Position(3)/2;
ysource = sA.Position(2)-30;
dtA.SourceEndPoint = [xsource ysource];
dtA.MidPoint = [xsource ysource+15];

% Add a default transition to state A1
dtA1 = Stateflow.Transition(ch);
dtA1.Destination = sA1;
dtA1.DestinationOClock = 0;
xsource = sA1.Position(1)+sA1.Position(3)/2;
ysource = sA1.Position(2)-30;
dtA1.SourceEndPoint = [xsource ysource];
dtA1.MidPoint = [xsource ysource+15];

sfsave(m.Name, 'myModel');