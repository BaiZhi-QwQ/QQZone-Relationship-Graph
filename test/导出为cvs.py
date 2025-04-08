from network.core.builder import QZoneNetworkBuilder

builder = QZoneNetworkBuilder()
builder.build_network()
print("社交网络构建完成！")
builder.export_for_cosmograph()