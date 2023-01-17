# Structural element

Structural element 为“结构”层级概念。
一个完整的可传力结构中，为实现节点自动连接，原则上应设置相同的 Structural element id。
此外，为方便管理，同一类 Structural element 一般设置相同的 Structural element id。
Structural element id 对应于Itasca命令行界面中的“id”关键字。

Structural element id 编码总则：

- 编码位数：3
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

# Structural component

Structural component 为“数值模型”层级概念。
Structural component 指FLAC<sup>3D</sup>中的结构单元Node、Link和各类Element(有限元意义)。
Structural component id 与FLAC<sup>3D</sup>内建的结构单元”component_id“属性存在对应关系，
但由于”component_id“由系统自动分配且无法指定，故此处所指 Structural component 为出于管理目的建立的孪生对象。
Structural component 拥有自定义的id编号，通过映射表与指FLAC<sup>3D</sup>内建”component_id“一一对应。

Structural component id 编码总则：

- 编码位数：12
- 基础偏移：900,0,000,00,000
- 第1~3位：对应于 Structural element id
- 第4位：对应于component类型：
    + Node：1
    + Link：2
    + Element-Beam：3
    + Element-Cable：4
    + Element-Pile：5
    + Element-Shell：6
    + Element-Liner：7
    + Element-Geogrid：8
- 第5~7位：环号
- 第8~9位：子元素编号(如一环锚杆中的一根)，仅对部分类型有效
- 第10~12位：component序号
- 存储方式：五元组(StruElemID, 类型, 环号，子元素编号，序号)

## Bolt(锚杆) (type:cable)

Bolt element 的 component id 编码规则(8~12位)：

- 第8~9位：锚杆编号(与BoltGroup的节点坐标数组顺序对应，一般为顺时针)
- 第10~12位：component序号(自起始节点至终止节点，一般为隧道由内向外)

## Arch(拱架) (type: beam)

Arch element 的 component id 编码规则(8~12位)：

- 第8~9位：固定为00
- 第10~12位：component序号(自起始节点至终止节点，一般为由右侧底部起逆时针)