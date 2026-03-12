#!/usr/bin/env python3
"""Export a textured GLB from an MMD-style Blender file.

Usage:
  blender -b -P scripts/export_mmd_textured_glb.py -- \
    --input-blend /path/to/model.blend \
    --output-glb /path/to/model.glb
"""

import argparse
import bpy


def parse_args() -> argparse.Namespace:
    argv = []
    if "--" in __import__("sys").argv:
        argv = __import__("sys").argv[__import__("sys").argv.index("--") + 1 :]

    parser = argparse.ArgumentParser(description="Export textured GLB from MMD-style blend")
    parser.add_argument("--input-blend", required=True, help="Input .blend path")
    parser.add_argument("--output-glb", required=True, help="Output .glb path")
    parser.add_argument("--mesh-name", default="派蒙_mesh", help="Primary mesh object name")
    parser.add_argument("--armature-name", default="派蒙_arm", help="Armature object name")
    parser.add_argument("--root-name", default="派蒙", help="Optional root empty object name")
    return parser.parse_args(argv)


def pick_base_image(mat: bpy.types.Material):
    if not mat or not mat.use_nodes or not mat.node_tree:
        return None

    tex_nodes = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and getattr(n, "image", None)]
    if not tex_nodes:
        return None

    for n in tex_nodes:
        name = (n.name or "").lower()
        if "mmd_base_tex" in name or "base" in name:
            return n.image

    def score(node):
        fp = (node.image.filepath or "").lower() if node.image else ""
        penalty = 0
        if "toon" in fp:
            penalty += 5
        if "sphere" in fp or "mc3" in fp:
            penalty += 3
        if fp.endswith(".bmp"):
            penalty += 2
        return penalty

    tex_nodes.sort(key=score)
    return tex_nodes[0].image


def build_gltf_material(src_mat: bpy.types.Material) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=f"{src_mat.name}_GLTF")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (260, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Roughness"].default_value = 0.75
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    img = pick_base_image(src_mat)
    if img is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.location = (-320, 120)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

        fp = (img.filepath or "").lower()
        has_alpha = fp.endswith(".png") or img.depth == 32
        if has_alpha:
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            if hasattr(mat, "blend_method"):
                mat.blend_method = "BLEND"

    return mat


def remap_materials() -> None:
    remap = {}
    for mat in list(bpy.data.materials):
        if mat.name.startswith("mmd_tools_rigid_"):
            continue
        remap[mat.name] = build_gltf_material(mat)

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            if slot.material and slot.material.name in remap:
                slot.material = remap[slot.material.name]


def pick_export_objects(args: argparse.Namespace):
    for obj in bpy.data.objects:
        obj.select_set(False)

    picked = []
    for name in (args.mesh_name, args.armature_name, args.root_name):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.select_set(True)
            picked.append(obj)

    if not picked:
        # Fallback: export all visible objects.
        for obj in bpy.context.view_layer.objects:
            if not obj.hide_get():
                obj.select_set(True)
                picked.append(obj)

    mesh_obj = bpy.data.objects.get(args.mesh_name)
    arm_obj = bpy.data.objects.get(args.armature_name)
    bpy.context.view_layer.objects.active = mesh_obj or arm_obj or (picked[0] if picked else None)


def export_glb(out_path: str) -> None:
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_cameras=False,
        export_lights=False,
    )


def main() -> None:
    args = parse_args()
    bpy.ops.wm.open_mainfile(filepath=args.input_blend)
    remap_materials()
    pick_export_objects(args)
    export_glb(args.output_glb)
    print(f"EXPORTED {args.output_glb}")


if __name__ == "__main__":
    main()
