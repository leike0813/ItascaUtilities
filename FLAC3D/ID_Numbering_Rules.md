# Structural element

Structural element 为“结构”层级概念。
一个完整的可传力结构中，为实现节点自动连接，原则上应设置相同的 Structural element id。
此外，为方便管理，同一类 Structural element 一般设置相同的 Structural element id。
Structural element id 对应于Itasca命令行界面中的“id”关键字，在程序中对应“eid”属性。

Structural element id (eid)编码总则：

- 编码位数：3(XXX)
- 基础偏移：900
- 最终编码为：基础偏移 + 类偏移 + 自增偏移

## Bolt(锚杆) (type:cable)

Bolt element id 编码规则：

- 类偏移：0
- 自增偏移范围：[1, 29]
- 每一组锚杆(相同长度)一般采用同一个id
- 若无特殊需求，同一环的不同组锚杆亦可采用同一个id
- 默认规则：每一组锚杆一个id，由BoltGroup管理，各环id相同

## Arch(拱架) (type: beam)

Arch element id 编码规则：

- 类偏移：30
- 自增偏移范围：[1, 19]
- 当一环拱架为一次性施加时，采用同一个id
- 当一环拱架分步施加时，若各段采用共节点的连接方式，则采用同一个id
- 当一环拱架分步施加时，以下情况可采用不同的id
    + 有分组显示的需求时
    + 需要定义特殊的连接方式时
- 默认规则：每一组拱架一个id，由ArchRing管理，各环id相同

## PileRoof(管棚) (type:beam)

PileRoof element id 编码规则：

- 类偏移：50
- 自增偏移范围：[1, 9]
- 每一环管棚采用同一个id
- 默认规则：每一组管棚一个id，由PileRoofRing管理，各环id相同

## TBM(隧道掘进机)
### Shield(盾壳) (type:liner)

Shield element id 编码规则：

- 类偏移：99
- 采用唯一id(999)

### CutterHead(刀盘) (type:liner)

CutterHead element id 编码规则：

- 类偏移：98
- 采用唯一id(998)

### DiskGroup(刀具组) (type:liner)

DiskGroup element id 编码规则：

- 类偏移：90
- 自增偏移范围：[1, 7]
- 同参数的刀具一般归为一个DiskGroup，采用相同的id

# Structural class

Structural class 为“孪生模型”层级概念。
Structural class 指为实现参数化建模而设计的管理对象，
包括Bolt(锚杆)、Arch(拱架)、PileRoof(管棚)等大类，
每一大类中又包含Ring(环)、Group(组)两个层级的子类。
用户通过建立Structural class 可方便地实现循环开挖及模型管理等功能。

Structural class id 编码总则：

- 编码位数：
    + Ring级：5(XXX,RR)
    + Group级：7(XXX,RR,GG)
- 基础偏移：900,00(,00)
- 第1~3位(XXX)：对应于 Structural element id
    + 对于BoltRing，由于其Structural element id由下级对象BoltGroup管理，
因此其第1~3位固定为900。
- 第2~3位(RR)：对应于Ring序号
- 第4~5位(GG)：对应于Group序号

## TBM structural class 的特别规定

待补充。

# Structural instance

Structural instance 为“孪生模型”层级概念。
Structural instance 为 Structural class 的实例，
由 Structural class 创建。
每一个 Structural instance 均对应着一个数值模型中的结构实体，
如 ArchRing_Instance 对应着一环拱架，BoltEntity 对应着一根锚杆等。
用户可通过 Structural instance 的接口便捷地实现模型的查询及后处理。

Structural instance id 编码总则：

- 编码位数：
    + Ring级：5+3(XXX,RR.iii)
    + Group级：7+6(XXX,RR,GG.iii,jjj)
    + BoltEntity:9+6(XXX,RR,GG,BB.iii,jjj)
- 基础偏移：900,00(,00).000
- 第1~3(5)位：对应于创建者的Structural class id
- BoltEntity的第8~9位(BB)：对应着一个BoltGroup中的第几根锚杆
- iii/jjj：对应于Ring/Group的实例序号

## TBM Structural instance 的特别规定

待补充。

# Structural component

Structural component 为“数值模型”层级概念。
Structural component 指FLAC<sup>3D</sup>中的结构单元Node、Link和各类Element(有限元意义)。
Structural component id 与FLAC<sup>3D</sup>内建的结构单元”component_id“属性存在对应关系，
但由于”component_id“由系统自动分配且无法指定，故此处所指 Structural component 为出于管理目的建立的孪生对象。
Structural component 拥有自定义的id编号，通过映射表与指FLAC<sup>3D</sup>内建”component_id“一一对应。

Structural component id 编码总则：

- 编码位数：13(TT,XXX,iii,BB.xxx)
- 基础偏移：10,900,000,00.000
- 第1~2位(TT)：对应于component类型：
    + Node：10
    + Link：20
    + Element-Beam：30
    + Element-Cable：40
    + Element-Pile：50
    + Element-Shell：60
    + Element-Liner：70
    + Element-Geogrid：80
- 第3~5位(XXX)：对应于 Structural element id
- 第6~8位(iii)：所属Ring级Structural instance的实例序号(环号)
- 第9~10位(BB)：子元素编号(如一环锚杆中的一根)，仅对部分类型有效
- 第11~13位(xxx)：component序号
- 存储方式：五元组(类型, StruElemID, 环号, 子元素编号, 序号)

## Bolt(锚杆) (type:cable)

Bolt element 的 component id 编码规则(9~13位)：

- 第9~10位(BB)：锚杆编号(与BoltGroup的节点坐标数组顺序对应，一般为顺时针)
- 第11~13位(xxx)：component序号(自起始节点至终止节点，一般为隧道由内向外)

## Arch(拱架) (type: beam)

Arch element 的 component id 编码规则(9~13位)：

- 第8~9位(BB)：固定为00
- 第11~13位(xxx)：component序号(自起始节点至终止节点，与ArchRing的节点坐标数组顺序对应)