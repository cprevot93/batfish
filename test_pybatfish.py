# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pybatfish",
# ]
# ///

from pybatfish.client.session import Session

# Assign a friendly name to your network and snapshot
NETWORK_NAME = "example_network"
SNAPSHOT_NAME = "example_snapshot"

SNAPSHOT_PATH = "networks/example/vdom"

bf = Session(host="localhost")
# Now create the network and initialize the snapshot
bf.set_network(NETWORK_NAME)
bf.init_snapshot(SNAPSHOT_PATH, name=SNAPSHOT_NAME, overwrite=True)

import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)
pd.set_option("display.max_colwidth", 160)

print("=== fileParseStatus ===")
fps = bf.q.fileParseStatus().answer().frame()
print(fps)
fps.to_csv("file_parse_status.csv", index=False)

print("\n=== parseWarning (ipension only) ===")
pw = bf.q.parseWarning().answer().frame()
if not pw.empty:
    pw.to_csv("parse_warnings.csv", index=False)
    ipension_pw = pw[pw["Filename"].str.contains("ipension", case=False, na=False)]
    print(f"ipension warning rows: {len(ipension_pw)} / total: {len(pw)}")
    print(ipension_pw.head(50))
else:
    print("(no parse warnings)")

print("\n=== nodeProperties (VRFs) ===")
np_ = bf.q.nodeProperties(properties="VRFs").answer().frame()
print(np_)

print("\n=== interfaceProperties for fg-ecs-ipension ===")
ifp = bf.q.interfaceProperties(nodes="fg-ecs-ipension-back-gva-cl204-m").answer().frame()
print(f"interface count: {len(ifp)}")
print(ifp[["Interface", "VRF"]].head(20) if not ifp.empty else "(none)")

print("\n=== routes software-factory:0 ===")
routes = bf.q.routes(vrfs="software-factory:0").answer().frame()
print(routes)
if not routes.empty:
    routes.to_csv("routes_sw.csv", index=False)

print("\n=== routes root:0 ===")
routes = bf.q.routes(vrfs="root:0").answer().frame()
print(routes)
if not routes.empty:
    routes.to_csv("routes_root.csv", index=False)

print("\n=== all routes for fg-ecs-ipension (any vrf) ===")
all_routes = bf.q.routes(nodes="fg-ecs-ipension-back-gva-cl204-m").answer().frame()
print(f"route count: {len(all_routes)}")
print(all_routes.head(30))
