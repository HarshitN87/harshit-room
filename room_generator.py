"""Harshit Room — RETIRED Blender pipeline (kept for provenance).

The project now builds 100% procedurally in Three.js on the room-3d-mvp
pipeline (see src/components/ + README). This script is no longer used to
produce the site and is kept only as a modelling reference.
"""
import bpy
import math
import os
import random


# ---------------------------------------------------------------- helpers
def clear_scene():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in bpy.data.objects:
        try:
            obj.hide_set(False)
            obj.hide_select = False
            obj.hide_viewport = False
        except Exception:
            pass
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.textures,
                 bpy.data.lights, bpy.data.cameras):
        for block in list(coll):
            if getattr(block, 'users', 1) == 0:
                try:
                    coll.remove(block)
                except Exception:
                    pass


def apply_transforms(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def add_bevel_modifier(obj, width=0.02, segments=3):
    try:
        modifier = obj.modifiers.new(name="Bevel", type='BEVEL')
        modifier.width = width
        modifier.segments = segments
        modifier.limit_method = 'ANGLE'
        modifier.angle_limit = 0.523599
    except Exception:
        pass


def enable_smooth_shading(obj, angle=0.523599):
    try:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if hasattr(bpy.ops.object, "shade_auto_smooth"):
            bpy.ops.object.shade_auto_smooth()
            if "Smooth by Angle" in obj.modifiers:
                try:
                    obj.modifiers["Smooth by Angle"]["Input_1"] = angle
                except Exception:
                    pass
        elif hasattr(obj.data, 'use_auto_smooth'):
            bpy.ops.object.shade_smooth()
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = angle
        else:
            bpy.ops.object.shade_smooth()
    except Exception:
        pass


def create_cube(name, location, scale, material=None, bevel_width=0.01):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    apply_transforms(obj)
    if bevel_width and bevel_width > 0:
        add_bevel_modifier(obj, width=bevel_width)
    enable_smooth_shading(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_cylinder(name, location, radius, depth, rotation=(0, 0, 0),
                    material=None, bevel_width=0.0, vertices=24,
                    end_fill='NGON'):
    try:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                            vertices=vertices,
                                            end_fill_type=end_fill,
                                            location=location)
    except TypeError:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                            location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    apply_transforms(obj)
    if bevel_width and bevel_width > 0:
        add_bevel_modifier(obj, width=bevel_width)
    enable_smooth_shading(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_sphere(name, location, radius, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location,
                                        segments=20, ring_count=12)
    obj = bpy.context.active_object
    obj.name = name
    apply_transforms(obj)
    enable_smooth_shading(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_torus(name, location, major_radius, minor_radius,
                 rotation=(0, 0, 0), material=None):
    """Detail rings (rod finials, mug handle, bucket rim, grommets)."""
    try:
        bpy.ops.mesh.primitive_torus_add(location=location,
                                         major_radius=major_radius,
                                         minor_radius=minor_radius,
                                         major_segments=28, minor_segments=12)
    except Exception:
        return create_cylinder(name, location, minor_radius * 2,
                               minor_radius * 2, rotation, material)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    apply_transforms(obj)
    enable_smooth_shading(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_hollow_bucket(name, location, radius, depth, material,
                         rib_mat=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth,
                                        end_fill_type='NOTHING',
                                        location=location)
    obj = bpy.context.active_object
    obj.name = name
    try:
        solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = 0.012
    except Exception:
        pass
    add_bevel_modifier(obj, width=0.003)
    enable_smooth_shading(obj)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius - 0.006, depth=0.01,
        location=(location[0], location[1], location[2] - depth / 2.0 + 0.005))
    bottom = bpy.context.active_object
    bottom.name = "%s_Bottom" % name
    enable_smooth_shading(bottom)
    bottom.parent = obj
    try:
        bottom.matrix_parent_inverse = obj.matrix_world.inverted()
    except Exception:
        pass
    if material:
        obj.data.materials.append(material)
        bottom.data.materials.append(material)
    # --- sub-detail, still the same bucket: rolled rim ---------------------
    rim = create_torus("%s_Rim" % name,
                       (location[0], location[1], location[2] + depth / 2.0),
                       radius, 0.009, (0, 0, 0), material or rib_mat)
    rim.parent = obj
    # --- sub-detail: vertical grip ribs ------------------------------------
    rmat = rib_mat or material
    for i in range(12):
        a = i * math.pi / 6.0
        rx = location[0] + (radius + 0.002) * math.cos(a)
        ry = location[1] + (radius + 0.002) * math.sin(a)
        rib = create_cube("%s_Rib_%02d" % (name, i), (rx, ry, location[2]),
                          (0.008, 0.008, depth * 0.42), material=rmat,
                          bevel_width=0.002)
        rib.rotation_euler[2] = -a
        rib.parent = obj
    # --- sub-detail: dark inner shadow disc (depth cue, same bucket) -------
    dark = create_cylinder("%s_InnerShadow" % name,
                           (location[0], location[1],
                            location[2] - depth / 2.0 + 0.02),
                           radius - 0.012, 0.004, material=rmat)
    try:
        dark.parent = obj
    except Exception:
        pass
    # --- sub-detail: foot ring ----------------------------------------------
    foot = create_torus("%s_FootRing" % name,
                        (location[0], location[1],
                         location[2] - depth / 2.0 + 0.008),
                        radius - 0.01, 0.006, (0, 0, 0), rmat)
    try:
        foot.parent = obj
    except Exception:
        pass
    return obj


# ---------------------------------------------------------------- materials
def set_principled_inputs(principled, inputs_dict):
    for key, val in inputs_dict.items():
        try:
            if key in principled.inputs:
                principled.inputs[key].default_value = val
            elif key == 'Emission Color' and 'Emission' in principled.inputs:
                principled.inputs['Emission'].default_value = val
        except Exception:
            pass


def _add_bump(nodes, links, principled, scale=40.0, strength=0.25):
    """Micro-surface bump so close-ups never look flat (Bruno-style)."""
    try:
        noise = nodes.new(type="ShaderNodeTexNoise")
        noise.inputs['Scale'].default_value = scale
        noise.inputs['Detail'].default_value = 3.0
        bump = nodes.new(type="ShaderNodeBump")
        bump.inputs['Strength'].default_value = strength
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], principled.inputs['Normal'])
        return noise
    except Exception:
        return None


def create_simple_material(name, color, roughness=0.5, metallic=0.0,
                           emission=None, emission_strength=1.0,
                           bump_scale=0.0, bump_strength=0.2):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    try:
        mat.diffuse_color = color
    except Exception:
        pass
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    if principled:
        inputs = {'Base Color': color, 'Roughness': roughness,
                  'Metallic': metallic}
        if emission:
            inputs['Emission Color'] = emission
            inputs['Emission Strength'] = emission_strength
        set_principled_inputs(principled, inputs)
        if bump_scale and bump_scale > 0:
            _add_bump(nodes, links, principled, bump_scale, bump_strength)
    return mat


def create_bedsheet_material():
    m = create_simple_material("BedsheetMat", (0.35, 0.45, 0.52, 1.0),
                               roughness=0.9, bump_scale=60.0,
                               bump_strength=0.12)
    # woven sheet: faint two-direction weave feel via second bump is overkill;
    # single fine noise reads as fabric at bake resolution.
    return m


def create_fabric_material(name, color, roughness=0.9, weave=70.0):
    return create_simple_material(name, color, roughness=roughness,
                                  bump_scale=weave, bump_strength=0.18)


def create_wood_material():
    mat = bpy.data.materials.new(name="WarmWood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    if not principled:
        return mat
    try:
        for link in list(principled.inputs['Base Color'].links):
            links.remove(link)
        wave = nodes.new(type="ShaderNodeTexWave")
        if hasattr(wave, 'wave_type'):
            wave.wave_type = 'BANDS'
        if hasattr(wave, 'bands_direction'):
            wave.bands_direction = 'X'
        elif hasattr(wave, 'direction'):
            wave.direction = 'X'
        wave.inputs['Scale'].default_value = 14.0
        wave.inputs['Distortion'].default_value = 1.8
        grain = nodes.new(type="ShaderNodeTexNoise")
        grain.inputs['Scale'].default_value = 28.0
        grain.inputs['Detail'].default_value = 4.0
        mix = nodes.new(type="ShaderNodeMixRGB")
        mix.blend_type = 'OVERLAY'
        mix.inputs['Fac'].default_value = 0.35
        links.new(wave.outputs['Color'], mix.inputs['Color1'])
        links.new(grain.outputs['Fac'], mix.inputs['Color2'])
        colorramp = nodes.new(type="ShaderNodeValToRGB")
        stops = colorramp.color_ramp.elements
        stops[0].color = (0.40, 0.22, 0.13, 1.0)
        stops[0].position = 0.0
        stops[1].color = (0.63, 0.41, 0.27, 1.0)
        stops[1].position = 1.0
        links.new(mix.outputs['Color'], colorramp.inputs['Fac'])
        links.new(colorramp.outputs['Color'], principled.inputs['Base Color'])
        # roughness variation so highlights break up like real walnut
        ramp2 = nodes.new(type="ShaderNodeValToRGB")
        ramp2.color_ramp.elements[0].position = 0.25
        ramp2.color_ramp.elements[1].position = 0.85
        links.new(grain.outputs['Fac'], ramp2.inputs['Fac'])
        try:
            principled.inputs['Roughness'].default_value = 0.32
            rough_mix = nodes.new(type="ShaderNodeMixRGB")
            rough_mix.blend_type = 'MIX'
            rough_mix.inputs['Fac'].default_value = 0.4
            rough_mix.inputs['Color1'].default_value = (0.28, 0.28, 0.28, 1.0)
            rough_mix.inputs['Color2'].default_value = (0.45, 0.45, 0.45, 1.0)
            links.new(ramp2.outputs['Color'], rough_mix.inputs['Fac'])
        except Exception:
            pass
        _add_bump(nodes, links, principled, scale=90.0, strength=0.08)
    except Exception:
        pass
    return mat


def create_wall_material():
    # warm off-white plaster: ultra-subtle mottling, never flat white
    m = create_simple_material("WallMat", (0.92, 0.90, 0.87, 1.0),
                               roughness=0.9, bump_scale=25.0,
                               bump_strength=0.06)
    return m


def create_floor_planks():
    """Starburst parquet tiles with grout, height + tone jitter (same tiles)."""
    floor_cream = create_simple_material("FloorCream", (0.62, 0.48, 0.36, 1.0),
                                         roughness=0.9, bump_scale=50.0,
                                         bump_strength=0.1)
    floor_tan = create_simple_material("FloorTan", (0.68, 0.54, 0.42, 1.0),
                                       roughness=0.9, bump_scale=50.0,
                                       bump_strength=0.1)
    floor_brown = create_simple_material("FloorBrown", (0.50, 0.35, 0.24, 1.0),
                                         roughness=0.92, bump_scale=50.0,
                                         bump_strength=0.1)
    floor_dark = create_simple_material("FloorDark", (0.32, 0.22, 0.16, 1.0),
                                        roughness=0.92, bump_scale=55.0,
                                        bump_strength=0.12)
    grout_mat = create_simple_material("FloorGrout", (0.23, 0.16, 0.11, 1.0),
                                       roughness=0.98)
    # grout bed under everything (still the floor, not a new object)
    create_cube("Floor_GroutBed", (0.0, 0.0, -0.018),
                (2.01, 2.01, 0.004), material=grout_mat, bevel_width=0.0)
    # thin outer skirt so floor edge has thickness from side views
    create_cube("Floor_Skirt_Front", (0.0, -2.0, -0.03),
                (2.0, 0.015, 0.03), material=grout_mat, bevel_width=0.001)
    create_cube("Floor_Skirt_Side", (2.0, 0.0, -0.03),
                (0.015, 2.0, 0.03), material=grout_mat, bevel_width=0.001)
    random.seed(105)
    for ix in range(5):
        tx = -1.6 + ix * 0.8
        for iy in range(5):
            ty = -1.6 + iy * 0.8
            jz = (random.random() - 0.5) * 0.003  # hand-laid height jitter
            jt = (random.random() - 0.5) * 0.03   # tonal jitter via scale
            create_cube("TileBase_%d_%d" % (ix, iy), (tx, ty, -0.01 + jz),
                        (0.395, 0.395, 0.005), material=floor_brown,
                        bevel_width=0.0012)
            diamond = create_cube("TileDiamond_%d_%d" % (ix, iy),
                                  (tx, ty, -0.008 + jz),
                                  (0.24 + jt * 0.2, 0.24 + jt * 0.2, 0.005),
                                  material=floor_cream, bevel_width=0.0012)
            diamond.rotation_euler[2] = 0.785398
            create_cube("TileCenter_%d_%d" % (ix, iy), (tx, ty, -0.006 + jz),
                        (0.12, 0.12, 0.005), material=floor_tan,
                        bevel_width=0.0012)
            for s in range(4):
                angle = s * math.pi / 4
                # alternate spoke lengths for pinwheel feel
                leng = 0.11 if s % 2 == 0 else 0.095
                spoke = create_cube(
                    "TileSpoke_%d_%d_%d" % (ix, iy, s), (tx, ty, -0.004 + jz),
                    (leng, 0.015, 0.005), material=floor_dark,
                    bevel_width=0.0006)
                spoke.rotation_euler[2] = angle
            # center pin dot (same tile family)
            create_cylinder("TilePin_%d_%d" % (ix, iy), (tx, ty, -0.003 + jz),
                            0.008, 0.004, material=floor_dark)


def bake_wood_texture(export_dir):
    """Bake procedural walnut into an image so GLB keeps its grain."""
    mat = bpy.data.materials.get("WarmWood")
    if not mat:
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    img_path = os.path.join(export_dir, "wood_baked.png")
    img = bpy.data.images.new("WarmWoodBaked", 1024, 1024)
    img.filepath_raw = img_path
    img.file_format = 'PNG'
    tex_node = nodes.new(type="ShaderNodeTexImage")
    tex_node.image = img
    nodes.active = tex_node
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -10))
    plane = bpy.context.active_object
    plane.name = "TempBakePlane"
    plane.data.materials.append(mat)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    orig_engine = bpy.context.scene.render.engine
    try:
        orig_samples = bpy.context.scene.cycles.samples
    except Exception:
        orig_samples = 16
    try:
        orig_device = bpy.context.scene.cycles.device
    except Exception:
        orig_device = 'CPU'
    bpy.context.scene.render.engine = 'CYCLES'
    try:
        bpy.context.scene.cycles.device = 'CPU'
        bpy.context.scene.cycles.samples = 1
    except Exception:
        pass
    colorramp = None
    for n in nodes:
        if n.type == 'VALTORGB':
            colorramp = n
            break
    principled = nodes.get("Principled BSDF")
    if colorramp and principled:
        emit_node = nodes.new(type="ShaderNodeEmission")
        links.new(colorramp.outputs['Color'], emit_node.inputs['Color'])
        output_node = None
        for n in nodes:
            if n.type == 'OUTPUT_MATERIAL':
                output_node = n
                break
        if output_node:
            orig_link = (output_node.inputs['Surface'].links[0].from_socket
                         if output_node.inputs['Surface'].links else None)
            links.new(emit_node.outputs['Emission'],
                      output_node.inputs['Surface'])
            try:
                bpy.ops.object.bake(type='EMIT')
                img.save()
            except Exception as e:
                print("wood bake failed: %s" % e)
            if orig_link:
                links.new(orig_link, output_node.inputs['Surface'])
            nodes.remove(emit_node)
    if principled:
        for link in list(principled.inputs['Base Color'].links):
            links.remove(link)
        links.new(tex_node.outputs['Color'],
                  principled.inputs['Base Color'])
    bpy.context.scene.render.engine = orig_engine
    try:
        bpy.context.scene.cycles.samples = orig_samples
        bpy.context.scene.cycles.device = orig_device
    except Exception:
        pass
    bpy.data.objects.remove(plane, do_unlink=True)


def bake_and_export_combined_glb(public_dir):
    import os as _os
    original_selection = [obj for obj in bpy.context.selected_objects]
    original_active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    mesh_objs = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            mesh_objs.append(obj)
    if not mesh_objs:
        print("No meshes found to bake!")
        return
    bpy.ops.object.duplicate()
    dup_objs = [obj for obj in bpy.context.selected_objects]
    for obj in mesh_objs:
        obj.hide_render = True
    bpy.context.view_layer.objects.active = dup_objs[0]
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    merged_obj.name = "Baked_Room_Mesh"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    if not _os.path.exists(public_dir):
        _os.makedirs(public_dir)
    img_path = _os.path.join(public_dir, "room_baked_combined.png")
    img = bpy.data.images.new("RoomBakedCombined", 4096, 4096)
    img.filepath_raw = img_path
    img.file_format = 'PNG'
    added_nodes = []
    for mat in bpy.data.materials:
        if mat.use_nodes:
            try:
                tex_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                tex_node.image = img
                mat.node_tree.nodes.active = tex_node
                added_nodes.append((mat, tex_node))
            except Exception:
                pass
    orig_engine = bpy.context.scene.render.engine
    try:
        orig_samples = bpy.context.scene.cycles.samples
    except Exception:
        orig_samples = 64
    try:
        orig_device = bpy.context.scene.cycles.device
    except Exception:
        orig_device = 'CPU'
    bpy.context.scene.render.engine = 'CYCLES'
    try:
        bpy.context.scene.cycles.samples = 128
    except Exception:
        pass
    print("Baking combined lighting (AO + shadows + emissive)...")
    try:
        bpy.ops.object.bake(type='COMBINED')
        img.save()
    except Exception as e:
        print("combined bake failed: %s" % e)
    baked_mat = bpy.data.materials.new(name="BakedRoomMaterial")
    baked_mat.use_nodes = True
    nodes = baked_mat.node_tree.nodes
    links = baked_mat.node_tree.links
    principled = nodes.get("Principled BSDF")
    if principled:
        nodes.remove(principled)
    tex_node_final = nodes.new(type="ShaderNodeTexImage")
    tex_node_final.image = img
    emit_node = nodes.new(type="ShaderNodeEmission")
    links.new(tex_node_final.outputs['Color'], emit_node.inputs['Color'])
    output_node = None
    for n in nodes:
        if n.type == 'OUTPUT_MATERIAL':
            output_node = n
            break
    if output_node:
        links.new(emit_node.outputs['Emission'], output_node.inputs['Surface'])
    merged_obj.data.materials.clear()
    merged_obj.data.materials.append(baked_mat)
    baked_glb_path = _os.path.join(public_dir, "room_baked_combined.glb")
    bpy.ops.object.select_all(action='DESELECT')
    merged_obj.select_set(True)
    bpy.context.view_layer.objects.active = merged_obj
    try:
        bpy.ops.export_scene.gltf(filepath=baked_glb_path,
                                  export_format='GLB', use_selection=True,
                                  export_materials='EXPORT')
        print("Exported baked combined GLB to: %s" % baked_glb_path)
    except Exception as e:
        print("Failed to export baked GLB: %s" % e)
    bpy.data.objects.remove(merged_obj, do_unlink=True)
    for mat, node in added_nodes:
        try:
            mat.node_tree.nodes.remove(node)
        except Exception:
            pass
    for obj in mesh_objs:
        obj.hide_render = False
    bpy.context.scene.render.engine = orig_engine
    try:
        bpy.context.scene.cycles.samples = orig_samples
        bpy.context.scene.cycles.device = orig_device
    except Exception:
        pass
    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selection:
        try:
            obj.select_set(True)
        except Exception:
            pass
    if original_active:
        bpy.context.view_layer.objects.active = original_active


def _export_paths():
    """Portable paths: repo root + public/ (works on any machine/Vercel)."""
    try:
        blend = bpy.data.filepath
        base = os.path.dirname(blend) if blend else os.getcwd()
    except Exception:
        base = os.getcwd()
    if not base:
        base = os.getcwd()
    public_dir = os.path.join(base, "public")
    return base, public_dir


def build_room():
    clear_scene()
    # ------------------------------------------------------------- materials
    bedsheet_mat = create_bedsheet_material()
    wood_mat = create_wood_material()
    wall_mat = create_wall_material()
    baseboard_mat = create_simple_material("BaseboardMat",
                                           (0.95, 0.95, 0.95, 1.0),
                                           roughness=0.35, bump_scale=30.0,
                                           bump_strength=0.05)
    window_frame_mat = create_simple_material("WindowFrameMat",
                                              (0.96, 0.96, 0.96, 1.0),
                                              roughness=0.28, bump_scale=30.0,
                                              bump_strength=0.04)
    glass_mat = create_simple_material("GlassMat", (0.55, 0.82, 0.95, 1.0),
                                       roughness=0.06,
                                       emission=(0.12, 0.22, 0.32, 1.0),
                                       emission_strength=0.6)
    metal_mat = create_simple_material("MetalMat", (0.85, 0.85, 0.85, 1.0),
                                       roughness=0.22, metallic=1.0,
                                       bump_scale=80.0, bump_strength=0.05)
    dark_metal_mat = create_simple_material("DarkMetalMat",
                                            (0.25, 0.25, 0.27, 1.0),
                                            roughness=0.4, metallic=0.9)
    black_plastic_mat = create_simple_material("BlackPlasticMat",
                                               (0.07, 0.07, 0.07, 1.0),
                                               roughness=0.5, bump_scale=45.0,
                                               bump_strength=0.08)
    grey_plastic_mat = create_simple_material("GreyPlasticMat",
                                              (0.28, 0.28, 0.28, 1.0),
                                              roughness=0.55, bump_scale=45.0,
                                              bump_strength=0.08)
    white_plastic_mat = create_simple_material("WhitePlasticMat",
                                               (0.93, 0.93, 0.93, 1.0),
                                               roughness=0.32, bump_scale=40.0,
                                               bump_strength=0.05)
    pink_curtain_mat = create_fabric_material("PinkCurtainMat",
                                              (0.92, 0.52, 0.62, 1.0))
    teal_curtain_mat = create_fabric_material("TealCurtainMat",
                                              (0.18, 0.58, 0.63, 1.0))
    red_bucket_mat = create_simple_material("RedBucketMat",
                                            (0.85, 0.12, 0.12, 1.0),
                                            roughness=0.38, bump_scale=40.0,
                                            bump_strength=0.1)
    slate_pillow_mat = create_fabric_material("SlatePillowMat",
                                              (0.42, 0.52, 0.60, 1.0),
                                              weave=80.0)
    purple_blanket_mat = create_fabric_material("PurpleBlanketMat",
                                                (0.35, 0.10, 0.55, 1.0),
                                                weave=65.0)
    screen_emit_mat = create_simple_material(
        "ScreenEmitMat", (0.05, 0.10, 0.15, 1.0), roughness=0.12,
        emission=(0.30, 0.70, 1.0, 1.0), emission_strength=5.0)
    cyan_led_mat = create_simple_material(
        "CyanLEDMat", (0.0, 1.0, 1.0, 1.0), roughness=0.2,
        emission=(0.0, 0.9, 1.0, 1.0), emission_strength=25.0)
    pink_led_mat = create_simple_material(
        "PinkLEDMat", (1.0, 0.0, 0.3, 1.0), roughness=0.2,
        emission=(1.0, 0.0, 0.3, 1.0), emission_strength=25.0)
    strong_white_led_mat = create_simple_material(
        "WhiteLEDMat", (1.0, 1.0, 0.9, 1.0), roughness=0.2,
        emission=(1.0, 1.0, 0.9, 1.0), emission_strength=20.0)
    bottle_mat = create_simple_material("BottleMat", (0.85, 0.80, 0.20, 1.0),
                                        roughness=0.18, bump_scale=35.0,
                                        bump_strength=0.04)
    bottle_glass_mat = create_simple_material(
        "BottleGlassMat", (0.75, 0.72, 0.35, 1.0), roughness=0.08,
        emission=(0.35, 0.33, 0.12, 1.0), emission_strength=0.7)
    water_mat = create_simple_material("WaterMat", (0.35, 0.65, 0.85, 1.0),
                                       roughness=0.05,
                                       emission=(0.15, 0.35, 0.55, 1.0),
                                       emission_strength=0.8)
    label_mat = create_simple_material("LabelMat", (0.94, 0.93, 0.88, 1.0),
                                       roughness=0.7, bump_scale=60.0,
                                       bump_strength=0.06)
    book_red_mat = create_simple_material("BookRedMat",
                                          (0.85, 0.15, 0.15, 1.0),
                                          roughness=0.75, bump_scale=55.0,
                                          bump_strength=0.1)
    book_teal_mat = create_simple_material("BookTealMat",
                                           (0.15, 0.65, 0.65, 1.0),
                                           roughness=0.75, bump_scale=55.0,
                                           bump_strength=0.1)
    book_yellow_mat = create_simple_material("BookYellowMat",
                                             (0.95, 0.75, 0.10, 1.0),
                                             roughness=0.75, bump_scale=55.0,
                                             bump_strength=0.1)
    pages_mat = create_simple_material("PagesMat", (0.93, 0.90, 0.82, 1.0),
                                       roughness=0.95, bump_scale=90.0,
                                       bump_strength=0.15)
    plant_pot_mat = create_simple_material("PlantPotMat",
                                           (0.95, 0.95, 0.93, 1.0),
                                           roughness=0.3, bump_scale=40.0,
                                           bump_strength=0.06)
    coffee_mat = create_simple_material("CoffeeMat", (0.16, 0.08, 0.04, 1.0),
                                        roughness=0.15,
                                        emission=(0.05, 0.02, 0.01, 1.0),
                                        emission_strength=0.4)
    mesh_mat = create_simple_material("ChairMeshMat", (0.10, 0.10, 0.11, 1.0),
                                      roughness=0.85, bump_scale=110.0,
                                      bump_strength=0.3)
    gap_mat = create_simple_material("GapShadowMat", (0.02, 0.02, 0.02, 1.0),
                                     roughness=1.0)
    screen_ui_dark = create_simple_material(
        "ScreenUIDark", (0.03, 0.05, 0.09, 1.0), roughness=0.4,
        emission=(0.05, 0.10, 0.20, 1.0), emission_strength=1.6)
    screen_ui_code = create_simple_material(
        "ScreenUICode", (0.20, 0.85, 1.0, 1.0), roughness=0.4,
        emission=(0.20, 0.75, 1.0, 1.0), emission_strength=3.0)
    screen_ui_accent = create_simple_material(
        "ScreenUIAccent", (1.0, 0.45, 0.75, 1.0), roughness=0.4,
        emission=(1.0, 0.30, 0.55, 1.0), emission_strength=3.0)

    # ---------------------------------------------------------------- floor
    create_floor_planks()

    # ---------------------------------------------------------------- walls
    create_cube("Wall_Left_Post1", (-2.025, -1.6, 1.5), (0.025, 0.4, 1.5),
                material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_Post2", (-2.025, 1.1, 1.5), (0.025, 0.9, 1.5),
                material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_UnderWindow", (-2.025, -0.5, 0.4),
                (0.025, 0.7, 0.4), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_AboveWindow", (-2.025, -0.5, 2.65),
                (0.025, 0.7, 0.35), material=wall_mat, bevel_width=0.0)
    # wall top caps (same walls, finished edge for orbit views)
    create_cube("Wall_Left_TopCap", (-2.025, -0.25, 3.0), (0.03, 2.28, 0.015),
                material=wall_mat, bevel_width=0.002)
    create_cube("Baseboard_Left", (-1.99, 0.0, 0.04), (0.01, 2.0, 0.04),
                material=baseboard_mat, bevel_width=0.002)
    create_cube("Baseboard_Left_Lip", (-1.985, 0.0, 0.082),
                (0.014, 2.0, 0.006), material=baseboard_mat,
                bevel_width=0.001)
    create_cube("Baseboard_Back_1", (-0.75, 1.99, 0.04), (1.25, 0.01, 0.04),
                material=baseboard_mat, bevel_width=0.002)
    create_cube("Baseboard_Back_1_Lip", (-0.75, 1.985, 0.082),
                (1.25, 0.014, 0.006), material=baseboard_mat,
                bevel_width=0.001)
    create_cube("Baseboard_Back_2", (1.75, 1.99, 0.04), (0.25, 0.01, 0.04),
                material=baseboard_mat, bevel_width=0.002)
    create_cube("Baseboard_Back_2_Lip", (1.75, 1.985, 0.082),
                (0.25, 0.014, 0.006), material=baseboard_mat,
                bevel_width=0.001)

    # ---------------------------------------------------------------- window
    create_cube("Window_Sill_Bottom", (-2.01, -0.5, 0.8),
                (0.02, 0.72, 0.015), material=window_frame_mat,
                bevel_width=0.005)
    create_cube("Window_Sill_Top", (-2.01, -0.5, 2.3), (0.02, 0.72, 0.015),
                material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Sill_Left", (-2.01, -1.2, 1.55), (0.02, 0.015, 0.75),
                material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Sill_Right", (-2.01, 0.2, 1.55), (0.02, 0.015, 0.75),
                material=window_frame_mat, bevel_width=0.005)
    # protruding sill nose (same window)
    create_cube("Window_SillNose", (-1.985, -0.5, 0.79),
                (0.035, 0.78, 0.012), material=window_frame_mat,
                bevel_width=0.004)
    # inner reveal liners give the opening real depth
    create_cube("Window_Reveal_Top", (-2.025, -0.5, 2.29),
                (0.028, 0.70, 0.012), material=window_frame_mat,
                bevel_width=0.002)
    create_cube("Window_Reveal_Bot", (-2.025, -0.5, 0.81),
                (0.028, 0.70, 0.012), material=window_frame_mat,
                bevel_width=0.002)
    # muntin cross (same window, classic 4-pane split)
    create_cube("Window_Muntin_V", (-2.008, -0.5, 1.55),
                (0.008, 0.012, 0.72), material=window_frame_mat,
                bevel_width=0.002)
    create_cube("Window_Muntin_H", (-2.008, -0.5, 1.55),
                (0.008, 0.69, 0.012), material=window_frame_mat,
                bevel_width=0.002)
    # architrave trim around opening (same window)
    create_cube("Window_Trim_Left", (-2.0, -1.23, 1.55),
                (0.012, 0.03, 1.56), material=window_frame_mat,
                bevel_width=0.003)
    create_cube("Window_Trim_Right", (-2.0, 0.23, 1.55),
                (0.012, 0.03, 1.56), material=window_frame_mat,
                bevel_width=0.003)
    create_cube("Window_Trim_Top", (-2.0, -0.5, 2.34),
                (0.012, 1.52, 0.03), material=window_frame_mat,
                bevel_width=0.003)
    # latch (same window hardware)
    create_cube("Window_Latch_Base", (-1.995, -0.5, 1.55),
                (0.012, 0.03, 0.05), material=metal_mat, bevel_width=0.002)
    latch = create_cube("Window_Latch_Lever", (-1.985, -0.47, 1.57),
                        (0.008, 0.05, 0.012), material=metal_mat,
                        bevel_width=0.002)
    latch.rotation_euler[2] = 0.5
    create_cube("Window_Glass", (-2.01, -0.5, 1.55), (0.005, 0.7, 0.73),
                material=glass_mat, bevel_width=0.0)
    # glass highlight streak (same pane, etched reflection cue)
    create_cube("Window_GlassStreak", (-2.004, -0.68, 1.62),
                (0.002, 0.05, 0.5), material=white_plastic_mat,
                bevel_width=0.0)

    # ------------------------------------------------------------ back wall
    create_cube("Wall_Back_Post1", (-0.75, 2.025, 1.5), (1.25, 0.025, 1.5),
                material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Back_Post2", (1.75, 2.025, 1.5), (0.25, 0.025, 1.5),
                material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Back_AboveDoor", (1.0, 2.025, 2.6),
                (0.5, 0.025, 0.4), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Back_TopCap", (0.0, 2.025, 3.0), (2.03, 0.03, 0.015),
                material=wall_mat, bevel_width=0.002)
    create_cube("DoorFrame_Left", (0.5, 2.01, 1.1), (0.015, 0.02, 1.1),
                material=window_frame_mat, bevel_width=0.005)
    create_cube("DoorFrame_Right", (1.5, 2.01, 1.1), (0.015, 0.02, 1.1),
                material=window_frame_mat, bevel_width=0.005)
    create_cube("DoorFrame_Top", (1.0, 2.01, 2.2), (0.515, 0.02, 0.015),
                material=window_frame_mat, bevel_width=0.005)
    # architrave (same door frame)
    create_cube("DoorFrame_ArchL", (0.485, 2.0, 1.1), (0.03, 0.012, 1.12),
                material=window_frame_mat, bevel_width=0.003)
    create_cube("DoorFrame_ArchR", (1.515, 2.0, 1.1), (0.03, 0.012, 1.12),
                material=window_frame_mat, bevel_width=0.003)
    theta = -0.436
    door_w, door_th, door_h = 0.485, 0.02, 1.09
    dx = 1.5 - door_w * math.cos(theta)
    dy = 2.0 - door_w * math.sin(theta)
    door = create_cube("DoorPanel", (dx, dy, 1.1), (door_w, door_th, door_h),
                       material=wood_mat, bevel_width=0.01)
    door.rotation_euler[2] = theta
    # recessed shaker panels (same door leaf)
    for _pz, _ph, _tag in ((1.45, 0.34, "Top"), (0.82, 0.42, "Bot")):
        px = dx - 0.0
        inset = create_cube("DoorPanel_Inset_%s" % _tag, (px, dy, _pz),
                            (door_w * 0.62, 0.006, _ph), material=wood_mat,
                            bevel_width=0.004)
        inset.rotation_euler[2] = theta
        rim = create_cube("DoorPanel_Rim_%s" % _tag, (px, dy, _pz),
                          (door_w * 0.72, 0.004, _ph + 0.06),
                          material=wood_mat, bevel_width=0.003)
        rim.rotation_euler[2] = theta
    # hinges (same door)
    for i, _hz in enumerate((0.65, 1.10, 1.70)):
        hx0 = 1.5 - 0.012
        hy0 = 2.0 - 0.012
        create_cylinder("Door_Hinge_%d" % i, (hx0, hy0, _hz), 0.011, 0.07,
                        material=dark_metal_mat)
        create_cube("Door_HingePlate_%d" % i, (hx0 - 0.02, hy0, _hz),
                    (0.025, 0.004, 0.055), material=dark_metal_mat,
                    bevel_width=0.001)
    hx = 1.5 - 2 * door_w * math.cos(theta)
    hy = 2.0 - 2 * door_w * math.sin(theta)
    handle = create_cube("DoorHandle", (hx, hy - 0.03 * math.cos(theta), 1.0),
                         (0.015, 0.04, 0.015), material=metal_mat,
                         bevel_width=0.003)
    handle.rotation_euler[2] = theta
    # rosettes + keyhole (same handle set)
    ros = create_cylinder("Door_Rosette_Out", (hx, hy - 0.012, 1.0), 0.022,
                          0.006, rotation=(1.5708, 0, 0), material=metal_mat)
    ros.rotation_euler[2] = theta
    create_cylinder("Door_Keyhole", (hx, hy - 0.012, 0.96), 0.007, 0.008,
                    rotation=(1.5708, 0, 0), material=dark_metal_mat)
    create_cube("Door_BottomGap", (dx, dy - 0.005, 0.045),
                (door_w * 0.98, 0.012, 0.045), material=gap_mat,
                bevel_width=0.0).rotation_euler.__setitem__(2, theta)

    # ------------------------------------------------------- curtain rod
    create_cylinder("WindowCurtainRod", (-1.95, -0.5, 2.45), radius=0.015,
                    depth=1.8, rotation=(1.5708, 0, 0), material=metal_mat)
    create_sphere("WindowCurtainRod_Finial_L", (-1.95, -1.42, 2.45), 0.028,
                  material=metal_mat)
    create_sphere("WindowCurtainRod_Finial_R", (-1.95, 0.42, 2.45), 0.028,
                  material=metal_mat)
    create_cube("WindowCurtainRod_Bracket_L", (-1.975, -1.25, 2.45),
                (0.03, 0.02, 0.02), material=dark_metal_mat,
                bevel_width=0.002)
    create_cube("WindowCurtainRod_Bracket_R", (-1.975, 0.25, 2.45),
                (0.03, 0.02, 0.02), material=dark_metal_mat,
                bevel_width=0.002)

    def create_wavy_curtain(name, start_y, end_y, x_center, material):
        steps = 26  # denser accordion (was 16)
        y_step = (end_y - start_y) / steps
        for i in range(steps):
            y = start_y + i * y_step + y_step / 2.0
            # two-frequency ripple: deep fold + fine ripple (Bruno-like)
            x_offset = (0.028 * math.sin(i * 1.35)
                        + 0.010 * math.sin(i * 2.9 + 0.7))
            z_lean = 0.012 * math.sin(i * 0.9)
            fold = create_cube(
                "%s_Fold_%02d" % (name, i),
                (x_center + x_offset, y, 1.45 + z_lean * 0.2),
                (0.016, y_step * 0.72, 0.95), material=material,
                bevel_width=0.003)
            fold.rotation_euler[0] = z_lean * 0.4
            # hem band at the bottom of every fold (same curtain)
            create_cube("%s_Hem_%02d" % (name, i),
                        (x_center + x_offset, y, 0.51),
                        (0.018, y_step * 0.72, 0.03), material=material,
                        bevel_width=0.002)
            # pinch pleat at the top (same curtain)
            create_cube("%s_Pleat_%02d" % (name, i),
                        (x_center + x_offset * 0.6, y, 2.36),
                        (0.012, y_step * 0.6, 0.10), material=material,
                        bevel_width=0.002)
            if i % 2 == 0:
                create_cube("%s_Loop_%02d" % (name, i),
                            (-1.94 + x_offset * 0.5, y, 2.43),
                            (0.02, 0.008, 0.03), material=material,
                            bevel_width=0.001)
                create_torus("%s_Ring_%02d" % (name, i),
                             (-1.95 + x_offset * 0.4, y, 2.45),
                             0.016, 0.0035, (0, 0, 0), metal_mat)

    create_wavy_curtain("PinkCurtain", -1.2, -0.7, -1.91, pink_curtain_mat)
    create_wavy_curtain("TealCurtain", -0.3, 0.2, -1.91, teal_curtain_mat)

    # ---------------------------------------------------------------- wardrobe
    create_cube("Wardrobe_Body", (-1.0, 1.7, 1.3), (0.8, 0.25, 1.3),
                material=wood_mat, bevel_width=0.01)
    create_cube("Wardrobe_Crown", (-1.0, 1.68, 2.62), (0.83, 0.28, 0.035),
                material=wood_mat, bevel_width=0.006)
    create_cube("Wardrobe_Plinth", (-1.0, 1.70, 0.035), (0.78, 0.24, 0.07),
                material=wood_mat, bevel_width=0.005)
    create_cube("Wardrobe_SideTrim_L", (-1.79, 1.55, 1.3),
                (0.015, 0.16, 2.2), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_SideTrim_R", (-0.21, 1.55, 1.3),
                (0.015, 0.16, 2.2), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Drawer_L", (-1.395, 1.44, 0.2), (0.38, 0.01, 0.12),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Drawer_L_Inset", (-1.395, 1.432, 0.2),
                (0.31, 0.004, 0.08), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Drawer_R", (-0.605, 1.44, 0.2), (0.38, 0.01, 0.12),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Drawer_R_Inset", (-0.605, 1.432, 0.2),
                (0.31, 0.004, 0.08), material=wood_mat, bevel_width=0.004)
    # drawer gap shadows (same drawers)
    create_cube("Wardrobe_Gap_Drawers", (-1.0, 1.435, 0.2),
                (0.79, 0.004, 0.008), material=gap_mat, bevel_width=0.0)
    create_cube("Wardrobe_Gap_Mid", (-1.0, 1.435, 1.35),
                (0.008, 0.004, 1.9), material=gap_mat, bevel_width=0.0)
    create_cube("Wardrobe_Door_LL", (-1.395, 1.44, 1.075), (0.38, 0.01, 0.675),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_LL_Inset", (-1.395, 1.432, 1.075),
                (0.31, 0.004, 0.60), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Door_LR", (-0.605, 1.44, 1.075), (0.38, 0.01, 0.675),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_LR_Inset", (-0.605, 1.432, 1.075),
                (0.31, 0.004, 0.60), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Door_UL", (-1.395, 1.44, 2.2), (0.38, 0.01, 0.35),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_UL_Inset", (-1.395, 1.432, 2.2),
                (0.31, 0.004, 0.28), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Door_UR", (-0.605, 1.44, 2.2), (0.38, 0.01, 0.35),
                material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_UR_Inset", (-0.605, 1.432, 2.2),
                (0.31, 0.004, 0.28), material=wood_mat, bevel_width=0.004)
    # inner bevel trim inside each inset (same doors, extra craft)
    for _tag, _zx, _zy in (("LL", -1.395, 1.075), ("LR", -0.605, 1.075)):
        create_cube("Wardrobe_Door_%s_Bead" % _tag, (_zx, 1.430, _zy),
                    (0.27, 0.003, 0.55), material=wood_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_LL", (-1.05, 1.42, 1.0), (0.01, 0.01, 0.08),
                material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_LR", (-0.95, 1.42, 1.0), (0.01, 0.01, 0.08),
                material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_UL", (-1.2, 1.42, 1.95), (0.06, 0.01, 0.01),
                material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_UR", (-0.8, 1.42, 1.95), (0.06, 0.01, 0.01),
                material=metal_mat, bevel_width=0.002)
    for _hx in (-1.05, -0.95):
        create_cylinder("Wardrobe_HandleBase_%s" % str(_hx), (_hx, 1.43, 1.0),
                        0.012, 0.008, rotation=(1.5708, 0, 0),
                        material=dark_metal_mat)
    create_cylinder("Wardrobe_LockPlate", (-0.95, 1.425, 1.15), radius=0.008,
                    depth=0.005, rotation=(1.5708, 0, 0), material=metal_mat)
    create_cylinder("Wardrobe_KeyShaft", (-0.95, 1.41, 1.15), radius=0.0018,
                    depth=0.025, rotation=(1.5708, 0, 0), material=metal_mat)
    create_torus("Wardrobe_KeyBow", (-0.95, 1.393, 1.15), 0.007, 0.0022,
                 (0, 0, 0), metal_mat)
    create_cube("Wardrobe_KeyTooth_0", (-0.95, 1.415, 1.142),
                (0.004, 0.006, 0.004), material=metal_mat, bevel_width=0.0)
    create_cube("Wardrobe_KeyTooth_1", (-0.95, 1.408, 1.158),
                (0.004, 0.006, 0.004), material=metal_mat, bevel_width=0.0)
    create_cylinder("Wardrobe_KeyHead", (-0.95, 1.395, 1.15), radius=0.006,
                    depth=0.003, rotation=(1.5708, 0, 0), material=metal_mat)

    # ------------------------------------------------------------------ bed
    create_cube("BedFrame_SideR", (-0.49, -0.3, 0.175), (0.02, 1.0, 0.175),
                material=wood_mat, bevel_width=0.01)
    create_cube("BedFrame_SideL", (-1.99, -0.3, 0.175), (0.02, 1.0, 0.175),
                material=wood_mat, bevel_width=0.01)
    create_cube("BedFrame_Front", (-1.24, -1.3, 0.175), (0.75, 0.02, 0.175),
                material=wood_mat, bevel_width=0.01)
    # legs (same frame)
    for _lx, _ly, _tag in ((-1.96, -1.27, "FL"), (-0.52, -1.27, "FR"),
                           (-1.96, 0.67, "BL"), (-0.52, 0.67, "BR")):
        create_cube("BedFrame_Leg_%s" % _tag, (_lx, _ly, 0.06),
                    (0.035, 0.035, 0.06), material=wood_mat,
                    bevel_width=0.006)
        create_cube("BedFrame_Foot_%s" % _tag, (_lx, _ly, 0.012),
                    (0.045, 0.045, 0.012), material=dark_metal_mat,
                    bevel_width=0.003)
    # rail top lips + slats (same frame)
    create_cube("BedFrame_Lip_R", (-0.49, -0.3, 0.27), (0.025, 1.0, 0.012),
                material=wood_mat, bevel_width=0.004)
    create_cube("BedFrame_Lip_L", (-1.99, -0.3, 0.27), (0.025, 1.0, 0.012),
                material=wood_mat, bevel_width=0.004)
    for i in range(5):
        create_cube("BedFrame_Slat_%d" % i, (-1.24, -1.05 + i * 0.38, 0.26),
                    (0.70, 0.05, 0.015), material=wood_mat, bevel_width=0.003)
    create_cube("Mattress", (-1.24, -0.3, 0.36), (0.73, 0.98, 0.09),
                material=bedsheet_mat, bevel_width=0.02)
    # mattress piping seams (same mattress)
    create_cube("Mattress_Piping_F", (-1.24, -1.272, 0.36),
                (0.725, 0.008, 0.012), material=white_plastic_mat,
                bevel_width=0.002)
    create_cube("Mattress_Piping_B", (-1.24, 0.672, 0.36),
                (0.725, 0.008, 0.012), material=white_plastic_mat,
                bevel_width=0.002)
    create_cube("Mattress_Piping_L", (-1.963, -0.3, 0.36),
                (0.008, 0.975, 0.012), material=white_plastic_mat,
                bevel_width=0.002)
    create_cube("Mattress_Piping_R", (-0.517, -0.3, 0.36),
                (0.008, 0.975, 0.012), material=white_plastic_mat,
                bevel_width=0.002)
    for i, (_bx, _by) in enumerate(((-1.5, -0.6), (-1.24, -0.6), (-0.98, -0.6),
                                    (-1.5, 0.0), (-1.24, 0.0), (-0.98, 0.0))):
        create_cylinder("Mattress_Button_%d" % i, (_bx, _by, 0.452),
                        0.007, 0.006, material=white_plastic_mat)
    # pillows with piping + dimple (same pillows)
    for _pname, _py, _rz in (("Pillow_1", 0.5, 0.06), ("Pillow_2", 0.18, -0.06)):
        p = create_cube(_pname, (-1.72, _py, 0.45), (0.15, 0.22, 0.035),
                        material=slate_pillow_mat, bevel_width=0.015)
        p.rotation_euler = (0.05, 0.0, _rz)
        create_cube("%s_Piping" % _pname, (-1.72, _py, 0.45),
                    (0.155, 0.225, 0.010), material=white_plastic_mat,
                    bevel_width=0.003)
        create_cylinder("%s_Dimple" % _pname, (-1.72, _py, 0.472),
                        0.018, 0.008, material=slate_pillow_mat)
    # blanket: top + hem + fold ridges + pleated drape (same blanket)
    create_cube("Blanket_Purple_Top", (-1.24, -0.2, 0.42),
                (0.73, 0.78, 0.02), material=purple_blanket_mat,
                bevel_width=0.015)
    create_cube("Blanket_Purple_Hem", (-1.24, -0.97, 0.415),
                (0.73, 0.025, 0.022), material=purple_blanket_mat,
                bevel_width=0.004)
    for i in range(6):
        _by = -0.52 + i * 0.115
        _bamp = 0.008 * math.sin(i * 1.4)
        ridge = create_cube("Blanket_Fold_%d" % i, (-1.24, _by, 0.435 + _bamp),
                            (0.70, 0.028, 0.014), material=purple_blanket_mat,
                            bevel_width=0.006)
        ridge.rotation_euler[2] = 0.03 * math.sin(i * 2.1)
    create_cube("Blanket_Purple_Drape", (-0.49, -0.2, 0.285),
                (0.01, 0.78, 0.135), material=purple_blanket_mat,
                bevel_width=0.015)
    for i in range(5):
        _dy = -0.48 + i * 0.14
        _dx = -0.482 + 0.006 * math.sin(i * 1.8)
        pleat = create_cube("Blanket_DrapeFold_%d" % i, (_dx, _dy, 0.285),
                            (0.012, 0.05, 0.13), material=purple_blanket_mat,
                            bevel_width=0.004)
        pleat.rotation_euler[0] = 0.06 * math.sin(i * 1.2)

    # ------------------------------------------------------------------ desk
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.2, 0.7, 0.0))
    desk_parent = bpy.context.active_object
    desk_parent.name = "Desk_Group"

    def addToDesk(obj):
        try:
            obj.parent = desk_parent
            obj.matrix_parent_inverse = desk_parent.matrix_world.inverted()
        except Exception:
            pass
        return obj

    addToDesk(create_cube("Desk_Top", (1.2, 0.7, 0.735), (0.75, 0.30, 0.015),
                          material=wood_mat, bevel_width=0.008))
    addToDesk(create_cube("Desk_Edge_Front", (1.2, 0.405, 0.735),
                          (0.75, 0.008, 0.016), material=wood_mat,
                          bevel_width=0.003))
    addToDesk(create_torus("Desk_Grommet_Ring", (1.62, 0.88, 0.745),
                           0.028, 0.005, (0, 0, 0), dark_metal_mat))
    addToDesk(create_cylinder("Desk_Grommet_Hole", (1.62, 0.88, 0.744),
                              0.024, 0.004, material=gap_mat))
    addToDesk(create_cube("Desk_Panel_Left", (0.46, 0.7, 0.36),
                          (0.015, 0.28, 0.36), material=wood_mat,
                          bevel_width=0.005))
    addToDesk(create_cube("Desk_Panel_Right", (1.94, 0.7, 0.36),
                          (0.015, 0.28, 0.36), material=wood_mat,
                          bevel_width=0.005))
    addToDesk(create_cube("Desk_PanelFoot_L", (0.46, 0.7, 0.012),
                          (0.02, 0.26, 0.012), material=dark_metal_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("Desk_PanelFoot_R", (1.94, 0.7, 0.012),
                          (0.02, 0.26, 0.012), material=dark_metal_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("Desk_Modesty_Back", (1.2, 0.96, 0.51),
                          (0.72, 0.015, 0.21), material=wood_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("Desk_Modesty_Notch", (1.2, 0.96, 0.63),
                          (0.18, 0.016, 0.03), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Desk_Keyboard_Tray", (1.1, 0.65, 0.66),
                          (0.45, 0.20, 0.01), material=wood_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("Desk_Tray_Rail_L", (0.66, 0.65, 0.66),
                          (0.012, 0.20, 0.012), material=dark_metal_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Desk_Tray_Rail_R", (1.54, 0.65, 0.66),
                          (0.012, 0.20, 0.012), material=dark_metal_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Desk_Tray_Lip", (1.1, 0.455, 0.668),
                          (0.45, 0.008, 0.014), material=wood_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Desk_Footrest_Shelf", (1.1, 0.7, 0.11),
                          (0.48, 0.22, 0.01), material=wood_mat,
                          bevel_width=0.003))
    for i in range(4):
        addToDesk(create_cube("Desk_Footrest_Grip_%d" % i,
                              (1.1, 0.60 + i * 0.055, 0.117),
                              (0.44, 0.012, 0.003), material=gap_mat,
                              bevel_width=0.0))
    addToDesk(create_cube("Desk_Footrest_Riser", (1.1, 0.50, 0.05),
                          (0.48, 0.01, 0.05), material=wood_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("Desk_Drawers_Box", (1.75, 0.7, 0.36),
                          (0.18, 0.28, 0.36), material=wood_mat,
                          bevel_width=0.005))
    addToDesk(create_cube("Desk_DrawerGap_Top", (1.75, 0.427, 0.55),
                          (0.176, 0.003, 0.006), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Desk_DrawerGap_Bot", (1.75, 0.427, 0.36),
                          (0.176, 0.003, 0.006), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Desk_Drawer_Top", (1.75, 0.43, 0.61),
                          (0.175, 0.005, 0.08), material=wood_mat,
                          bevel_width=0.004))
    addToDesk(create_cube("Desk_Drawer_Inset", (1.75, 0.427, 0.61),
                          (0.14, 0.003, 0.055), material=wood_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Desk_Drawer_Handle_Top", (1.75, 0.42, 0.61),
                          (0.05, 0.005, 0.006), material=metal_mat,
                          bevel_width=0.002))
    for _sx in (1.728, 1.772):
        addToDesk(create_cylinder("Desk_HandlePost_%s" % str(_sx),
                                  (_sx, 0.425, 0.61), 0.004, 0.012,
                                  rotation=(1.5708, 0, 0),
                                  material=dark_metal_mat))
    addToDesk(create_cylinder("Desk_Drawer_Lock", (1.88, 0.44, 0.66),
                              radius=0.005, depth=0.005,
                              rotation=(1.5708, 0, 0), material=metal_mat))
    addToDesk(create_cube("Desk_Cabinet_Door", (1.75, 0.43, 0.265),
                          (0.175, 0.005, 0.22), material=wood_mat,
                          bevel_width=0.004))
    addToDesk(create_cube("Desk_Cabinet_Inset", (1.75, 0.427, 0.265),
                          (0.14, 0.003, 0.17), material=wood_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Desk_Cabinet_Handle", (1.58, 0.42, 0.265),
                          (0.006, 0.005, 0.05), material=metal_mat,
                          bevel_width=0.002))

    # ----------------------------------------------------------------- chair
    create_cube("Chair_Hub", (0.35, 0.95, 0.08), (0.05, 0.05, 0.025),
                material=black_plastic_mat, bevel_width=0.005)
    create_cylinder("Chair_HubCap", (0.35, 0.95, 0.095), 0.032, 0.012,
                    material=grey_plastic_mat)
    for i in range(5):
        angle = i * 2 * math.pi / 5
        lx = 0.35 + 0.26 * math.cos(angle)
        ly = 0.95 + 0.26 * math.sin(angle)
        leg = create_cube("Chair_Leg_%d" % i, (lx, ly, 0.08),
                          (0.13, 0.025, 0.018), material=black_plastic_mat,
                          bevel_width=0.004)
        leg.rotation_euler[2] = angle
        # fork yoke holding each twin wheel (same legs)
        fx = 0.35 + 0.315 * math.cos(angle)
        fy = 0.95 + 0.315 * math.sin(angle)
        fork = create_cube("Chair_Fork_%d" % i, (fx, fy, 0.055),
                           (0.02, 0.05, 0.03), material=black_plastic_mat,
                           bevel_width=0.003)
        fork.rotation_euler[2] = angle
        create_cylinder("Chair_Axle_%d" % i, (fx, fy, 0.04), 0.006, 0.055,
                        rotation=(1.5708, 0, angle), material=dark_metal_mat)
        wx1 = 0.35 + 0.33 * math.cos(angle) - 0.018 * math.sin(angle)
        wy1 = 0.95 + 0.33 * math.sin(angle) + 0.018 * math.cos(angle)
        create_cylinder("Chair_Wheel_A_%d" % i, (wx1, wy1, 0.04),
                        radius=0.035, depth=0.018,
                        rotation=(1.5708, 0, angle),
                        material=black_plastic_mat)
        create_cylinder("Chair_WheelHub_A_%d" % i, (wx1, wy1, 0.04),
                        radius=0.012, depth=0.020,
                        rotation=(1.5708, 0, angle),
                        material=grey_plastic_mat)
        wx2 = 0.35 + 0.33 * math.cos(angle) + 0.018 * math.sin(angle)
        wy2 = 0.95 + 0.33 * math.sin(angle) - 0.018 * math.cos(angle)
        create_cylinder("Chair_Wheel_B_%d" % i, (wx2, wy2, 0.04),
                        radius=0.035, depth=0.018,
                        rotation=(1.5708, 0, angle),
                        material=black_plastic_mat)
        create_cylinder("Chair_WheelHub_B_%d" % i, (wx2, wy2, 0.04),
                        radius=0.012, depth=0.020,
                        rotation=(1.5708, 0, angle),
                        material=grey_plastic_mat)
    create_cylinder("Chair_Cylinder", (0.35, 0.95, 0.26), radius=0.03,
                    depth=0.22, material=metal_mat)
    create_cylinder("Chair_GasRing_Top", (0.35, 0.95, 0.33), 0.034, 0.012,
                    material=dark_metal_mat)
    create_cylinder("Chair_GasRing_Bot", (0.35, 0.95, 0.20), 0.034, 0.012,
                    material=dark_metal_mat)
    create_cylinder("Chair_Sheath", (0.35, 0.95, 0.17), radius=0.045,
                    depth=0.10, material=black_plastic_mat)
    create_cube("Chair_Seat", (0.35, 0.95, 0.46), (0.27, 0.27, 0.04),
                material=black_plastic_mat, bevel_width=0.012)
    # seat piping (same seat)
    create_cube("Chair_Seat_Piping_F", (0.35, 1.215, 0.46),
                (0.265, 0.008, 0.008), material=grey_plastic_mat,
                bevel_width=0.002)
    create_cube("Chair_Seat_Piping_B", (0.35, 0.685, 0.46),
                (0.265, 0.008, 0.008), material=grey_plastic_mat,
                bevel_width=0.002)
    create_cube("Chair_Seat_Piping_L", (0.085, 0.95, 0.46),
                (0.008, 0.265, 0.008), material=grey_plastic_mat,
                bevel_width=0.002)
    create_cube("Chair_Seat_Piping_R", (0.615, 0.95, 0.46),
                (0.008, 0.265, 0.008), material=grey_plastic_mat,
                bevel_width=0.002)
    for i, (_qx, _qy) in enumerate(((0.25, 0.85), (0.45, 0.85),
                                    (0.25, 1.05), (0.45, 1.05))):
        create_cylinder("Chair_SeatQuilt_%d" % i, (_qx, _qy, 0.482),
                        0.010, 0.006, material=black_plastic_mat)
    create_cube("Chair_Seat_BolsterL", (0.35, 1.21, 0.48),
                (0.27, 0.025, 0.025), material=black_plastic_mat,
                bevel_width=0.005)
    create_cube("Chair_Seat_BolsterR", (0.35, 0.69, 0.48),
                (0.27, 0.025, 0.025), material=black_plastic_mat,
                bevel_width=0.005)
    create_cube("Chair_TiltLever", (0.48, 0.80, 0.42), (0.09, 0.012, 0.012),
                material=dark_metal_mat, bevel_width=0.002)
    create_sphere("Chair_TiltKnob", (0.525, 0.80, 0.42), 0.014,
                  material=black_plastic_mat)
    create_cube("Chair_Arm_Left_Support", (0.35, 1.23, 0.57),
                (0.018, 0.018, 0.10), material=black_plastic_mat,
                bevel_width=0.002)
    create_cube("Chair_Arm_Left_Pad", (0.38, 1.23, 0.675),
                (0.12, 0.035, 0.018), material=black_plastic_mat,
                bevel_width=0.004)
    create_cube("Chair_Arm_Right_Support", (0.35, 0.67, 0.57),
                (0.018, 0.018, 0.10), material=black_plastic_mat,
                bevel_width=0.002)
    create_cube("Chair_Arm_Right_Pad", (0.38, 0.67, 0.675),
                (0.12, 0.035, 0.018), material=black_plastic_mat,
                bevel_width=0.004)
    for i, (_ax, _ay) in enumerate(((0.34, 1.23), (0.42, 1.23),
                                    (0.34, 0.67), (0.42, 0.67))):
        create_cylinder("Chair_ArmPad_Screw_%d" % i, (_ax, _ay, 0.685),
                        0.005, 0.004, material=dark_metal_mat)
    create_cube("Chair_Back_Support", (0.10, 0.95, 0.60),
                (0.018, 0.030, 0.17), material=black_plastic_mat,
                bevel_width=0.004)
    create_cube("Chair_Back_Frame_L", (0.12, 0.70, 0.82),
                (0.025, 0.018, 0.34), material=black_plastic_mat,
                bevel_width=0.006)
    create_cube("Chair_Back_Frame_R", (0.12, 1.20, 0.82),
                (0.025, 0.018, 0.34), material=black_plastic_mat,
                bevel_width=0.006)
    create_cube("Chair_Back_Frame_Top", (0.12, 0.95, 1.14),
                (0.025, 0.27, 0.018), material=black_plastic_mat,
                bevel_width=0.006)
    create_cube("Chair_Back_Frame_Bot", (0.12, 0.95, 0.50),
                (0.025, 0.27, 0.018), material=black_plastic_mat,
                bevel_width=0.006)
    create_cube("Chair_Back_Mesh", (0.125, 0.95, 0.82), (0.012, 0.245, 0.31),
                material=mesh_mat, bevel_width=0.0)
    # lumbar ribs across the mesh (same backrest)
    for i in range(5):
        create_cube("Chair_BackRib_%d" % i, (0.132, 0.95, 0.62 + i * 0.10),
                    (0.006, 0.235, 0.012), material=black_plastic_mat,
                    bevel_width=0.002)
    create_cube("Chair_LumbarPad", (0.135, 0.95, 0.72), (0.014, 0.16, 0.07),
                material=black_plastic_mat, bevel_width=0.008)
    create_cube("Chair_Headrest", (0.12, 0.95, 1.21), (0.025, 0.16, 0.075),
                material=black_plastic_mat, bevel_width=0.012)
    create_cube("Chair_Headrest_Post_L", (0.12, 0.90, 1.165),
                (0.012, 0.012, 0.03), material=dark_metal_mat,
                bevel_width=0.002)
    create_cube("Chair_Headrest_Post_R", (0.12, 1.00, 1.165),
                (0.012, 0.012, 0.03), material=dark_metal_mat,
                bevel_width=0.002)

    # ------------------------------------------------------- desk props
    addToDesk(create_cube("DeskMat", (1.1, 0.68, 0.745), (0.2, 0.25, 0.003),
                          material=black_plastic_mat, bevel_width=0.0))
    addToDesk(create_cube("DeskMat_Stitch_F", (1.1, 0.435, 0.746),
                          (0.195, 0.004, 0.001), material=grey_plastic_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("DeskMat_Stitch_B", (1.1, 0.925, 0.746),
                          (0.195, 0.004, 0.001), material=grey_plastic_mat,
                          bevel_width=0.0))
    # laptop (same unit, fully dressed)
    addToDesk(create_cube("Laptop_Base", (1.05, 0.65, 0.753),
                          (0.15, 0.11, 0.008), material=black_plastic_mat,
                          bevel_width=0.002))
    addToDesk(create_cube("Laptop_Foot_F_L", (0.93, 0.56, 0.744),
                          (0.015, 0.015, 0.004), material=gap_mat,
                          bevel_width=0.001))
    addToDesk(create_cube("Laptop_Foot_F_R", (1.17, 0.56, 0.744),
                          (0.015, 0.015, 0.004), material=gap_mat,
                          bevel_width=0.001))
    addToDesk(create_cube("Laptop_Port_L", (0.898, 0.65, 0.752),
                          (0.004, 0.03, 0.006), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Laptop_Port_R", (1.202, 0.65, 0.752),
                          (0.004, 0.02, 0.006), material=gap_mat,
                          bevel_width=0.0))
    scr = addToDesk(create_cube("Laptop_Screen", (1.05, 0.75, 0.865),
                                (0.14, 0.008, 0.11), material=black_plastic_mat,
                                bevel_width=0.002))
    scr.rotation_euler[0] = -0.32
    addToDesk(create_cylinder("Laptop_Hinge_L", (0.93, 0.745, 0.775),
                              0.008, 0.03, rotation=(0, 1.5708, 0),
                              material=dark_metal_mat))
    addToDesk(create_cylinder("Laptop_Hinge_R", (1.17, 0.745, 0.775),
                              0.008, 0.03, rotation=(0, 1.5708, 0),
                              material=dark_metal_mat))
    disp = addToDesk(create_cube("Laptop_Display", (1.05, 0.742, 0.865),
                                 (0.13, 0.002, 0.10), material=screen_emit_mat,
                                 bevel_width=0.0))
    disp.rotation_euler[0] = -0.32
    # bezel + webcam (same screen)
    bez = addToDesk(create_cube("Laptop_Bezel", (1.05, 0.7435, 0.865),
                                (0.136, 0.001, 0.106), material=gap_mat,
                                bevel_width=0.0))
    bez.rotation_euler[0] = -0.32
    cam = addToDesk(create_cylinder("Laptop_Webcam", (1.05, 0.7415, 0.912),
                                    0.0025, 0.002, rotation=(1.5708, 0, 0),
                                    material=screen_ui_dark))
    cam.rotation_euler[0] = -0.32
    # baked screen UI: menu bar + code lines (same display, reads as OS)
    ui_items = [("Laptop_UI_Bar", -0.036, 0.012, 0.120, screen_ui_dark),
                ("Laptop_UI_Line0", -0.020, 0.008, 0.090, screen_ui_code),
                ("Laptop_UI_Line1", -0.008, 0.008, 0.105, screen_ui_code),
                ("Laptop_UI_Line2", 0.004, 0.008, 0.060, screen_ui_accent),
                ("Laptop_UI_Line3", 0.016, 0.008, 0.100, screen_ui_code),
                ("Laptop_UI_Line4", 0.028, 0.008, 0.075, screen_ui_code),
                ("Laptop_UI_Dock", 0.042, 0.010, 0.110, screen_ui_dark)]
    for _n, _dz, _hh, _ww, _mm in ui_items:
        _item = addToDesk(create_cube(_n, (1.05, 0.7405, 0.865 + _dz),
                                      (_ww, 0.0012, _hh), material=_mm,
                                      bevel_width=0.0))
        _item.rotation_euler[0] = -0.32
    addToDesk(create_cube("Laptop_KB_Recess", (1.05, 0.59, 0.758),
                          (0.12, 0.045, 0.001), material=black_plastic_mat,
                          bevel_width=0.0))
    for r in range(5):
        for c in range(10):
            if r == 4 and 3 <= c <= 6:
                continue  # spacebar zone handled below
            kx = 1.05 - 0.099 + c * 0.022
            ky = 0.59 - 0.036 + r * 0.018
            if (r + c) % 8 == 0:
                key_col = (0.95, 0.40, 0.10, 1.0)
            else:
                key_col = (0.16, 0.16, 0.18, 1.0)
            k_mat = create_simple_material("LaptopKey_%d_%d" % (r, c),
                                           key_col, roughness=0.6,
                                           bump_scale=60.0, bump_strength=0.05)
            addToDesk(create_cube("LaptopKey_%d_%d" % (r, c), (kx, ky, 0.760),
                                  (0.009, 0.012, 0.002), material=k_mat,
                                  bevel_width=0.0005))
    space_mat = create_simple_material("LaptopKey_Space", (0.16, 0.16, 0.18, 1.0),
                                       roughness=0.6)
    addToDesk(create_cube("LaptopKey_Space", (1.05, 0.626, 0.760),
                          (0.075, 0.012, 0.002), material=space_mat,
                          bevel_width=0.0005))
    addToDesk(create_cube("Laptop_Touchpad", (1.05, 0.685, 0.7575),
                          (0.055, 0.032, 0.001), material=grey_plastic_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Laptop_TouchClick", (1.05, 0.672, 0.7576),
                          (0.055, 0.002, 0.001), material=gap_mat,
                          bevel_width=0.0))
    # mouse (same unit: wheel + seam + sensor)
    addToDesk(create_cube("Mouse", (1.18, 0.65, 0.755),
                          (0.04, 0.024, 0.015), material=black_plastic_mat,
                          bevel_width=0.005))
    addToDesk(create_cylinder("Mouse_Wheel", (1.18, 0.655, 0.765),
                              0.006, 0.010, rotation=(0, 1.5708, 0),
                              material=grey_plastic_mat))
    addToDesk(create_cube("Mouse_Seam", (1.18, 0.648, 0.7625),
                          (0.036, 0.0015, 0.001), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cylinder("Mouse_Sensor", (1.18, 0.648, 0.7475),
                              0.005, 0.002, material=cyan_led_mat))
    addToDesk(create_cube("Mouse_Cable", (1.18, 0.72, 0.748),
                          (0.004, 0.09, 0.003), material=black_plastic_mat,
                          bevel_width=0.001))

    # lamp (same unit, articulated + wired)
    addToDesk(create_cylinder("Lamp_Base", (1.45, 0.85, 0.75), radius=0.04,
                              depth=0.01, material=black_plastic_mat))
    addToDesk(create_torus("Lamp_BaseFelt", (1.45, 0.85, 0.7445),
                           0.032, 0.003, (0, 0, 0), gap_mat))
    addToDesk(create_cylinder("Lamp_BaseStem", (1.45, 0.85, 0.76),
                              radius=0.009, depth=0.02, material=dark_metal_mat))
    addToDesk(create_cylinder("Lamp_Neck_Lower", (1.46, 0.85, 0.84),
                              radius=0.006, depth=0.18, rotation=(0, 0.3, 0),
                              material=metal_mat))
    addToDesk(create_cylinder("Lamp_Spring_L", (1.468, 0.85, 0.84),
                              radius=0.009, depth=0.12, rotation=(0, 0.3, 0),
                              material=dark_metal_mat))
    addToDesk(create_cylinder("Lamp_Cable_Lower", (1.452, 0.85, 0.83),
                              radius=0.0022, depth=0.20, rotation=(0, 0.32, 0),
                              material=black_plastic_mat))
    addToDesk(create_cylinder("Lamp_Joint_1", (1.485, 0.85, 0.925),
                              radius=0.01, depth=0.016,
                              rotation=(1.5708, 0, 0),
                              material=black_plastic_mat))
    addToDesk(create_cylinder("Lamp_JointWasher_1", (1.485, 0.862, 0.925),
                              radius=0.006, depth=0.003,
                              rotation=(1.5708, 0, 0), material=metal_mat))
    addToDesk(create_cylinder("Lamp_Neck_Upper", (1.43, 0.85, 1.01),
                              radius=0.006, depth=0.16, rotation=(0, -0.6, 0),
                              material=metal_mat))
    addToDesk(create_cylinder("Lamp_Spring_U", (1.438, 0.85, 1.01),
                              radius=0.009, depth=0.10, rotation=(0, -0.6, 0),
                              material=dark_metal_mat))
    addToDesk(create_cylinder("Lamp_Cable_Upper", (1.442, 0.85, 1.005),
                              radius=0.0022, depth=0.18, rotation=(0, -0.62, 0),
                              material=black_plastic_mat))
    addToDesk(create_cylinder("Lamp_Joint_2", (1.355, 0.85, 1.08),
                              radius=0.008, depth=0.016,
                              rotation=(1.5708, 0, 0),
                              material=black_plastic_mat))
    addToDesk(create_cylinder("Lamp_Shade", (1.33, 0.85, 1.05), radius=0.045,
                              depth=0.05, rotation=(0, 0.8, 0),
                              material=black_plastic_mat, bevel_width=0.01))
    addToDesk(create_cylinder("Lamp_ShadeInner", (1.328, 0.85, 1.048),
                              radius=0.040, depth=0.006, rotation=(0, 0.8, 0),
                              material=white_plastic_mat))
    addToDesk(create_cylinder("Lamp_ShadeRim", (1.308, 0.85, 1.038),
                              radius=0.042, depth=0.004, rotation=(0, 0.8, 0),
                              material=dark_metal_mat))
    addToDesk(create_cylinder("Lamp_Bulb", (1.32, 0.85, 1.04), radius=0.038,
                              depth=0.008, rotation=(0, 0.8, 0),
                              material=strong_white_led_mat))
    addToDesk(create_cylinder("Lamp_Filament", (1.318, 0.85, 1.039),
                              radius=0.006, depth=0.004, rotation=(0, 0.8, 0),
                              material=strong_white_led_mat))
    addToDesk(create_cube("Lamp_Switch", (1.462, 0.85, 0.752),
                          (0.012, 0.008, 0.004), material=cyan_led_mat,
                          bevel_width=0.001))
    addToDesk(create_cube("Lamp_Cable_Desk", (1.50, 0.88, 0.747),
                          (0.10, 0.004, 0.003), material=black_plastic_mat,
                          bevel_width=0.001))

    # bottle (same unit: glass + liquid + label + knurled cap)
    addToDesk(create_cylinder("WaterBottle", (1.65, 0.85, 0.84), radius=0.04,
                              depth=0.18, material=bottle_glass_mat))
    addToDesk(create_cylinder("WaterBottle_Liquid", (1.65, 0.85, 0.815),
                              radius=0.034, depth=0.12, material=water_mat))
    addToDesk(create_cylinder("WaterBottle_Label", (1.65, 0.85, 0.83),
                              radius=0.0415, depth=0.06, material=label_mat))
    addToDesk(create_cube("WaterBottle_LabelStripe", (1.65, 0.809, 0.83),
                          (0.012, 0.004, 0.055), material=bottle_mat,
                          bevel_width=0.0))
    addToDesk(create_cylinder("WaterBottle_Neck", (1.65, 0.85, 0.935),
                              radius=0.022, depth=0.02, material=bottle_glass_mat))
    addToDesk(create_cylinder("WaterBottle_Cap", (1.65, 0.85, 0.955),
                              radius=0.025, depth=0.022, material=metal_mat))
    for i in range(8):
        _a = i * math.pi / 4
        _cx = 1.65 + 0.025 * math.cos(_a)
        _cy = 0.85 + 0.025 * math.sin(_a)
        addToDesk(create_cube("WaterBottle_CapRib_%d" % i, (_cx, _cy, 0.955),
                              (0.003, 0.003, 0.020), material=dark_metal_mat,
                              bevel_width=0.0))
    addToDesk(create_cylinder("WaterBottle_Punt", (1.65, 0.85, 0.752),
                              radius=0.028, depth=0.004, material=gap_mat))

    # charger (same unit: brick + prongs + LED + cable run)
    addToDesk(create_cube("ChargerBrick", (0.9, 0.85, 0.75),
                          (0.025, 0.035, 0.015), material=white_plastic_mat,
                          bevel_width=0.003))
    addToDesk(create_cube("ChargerBrick_Seam", (0.9, 0.85, 0.75),
                          (0.026, 0.036, 0.002), material=gap_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Charger_Prong_A", (0.9, 0.87, 0.762),
                          (0.003, 0.003, 0.012), material=metal_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Charger_Prong_B", (0.9, 0.83, 0.762),
                          (0.003, 0.003, 0.012), material=metal_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Charger_LED", (0.913, 0.85, 0.752),
                          (0.002, 0.006, 0.003), material=cyan_led_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Charger_Cable_0", (0.9, 0.80, 0.746),
                          (0.004, 0.06, 0.003), material=black_plastic_mat,
                          bevel_width=0.001))
    addToDesk(create_cube("Charger_Cable_1", (0.97, 0.77, 0.746),
                          (0.10, 0.004, 0.003), material=black_plastic_mat,
                          bevel_width=0.001))
    addToDesk(create_cube("Charger_Cable_2", (1.01, 0.70, 0.746),
                          (0.004, 0.10, 0.003), material=black_plastic_mat,
                          bevel_width=0.001))

    # books (same 3 volumes, now with pages + spine + bands)
    book_defs = [("DeskBook_1", 0.75, 0.88, 0.765, 0.11, 0.08, 0.030, 0.15,
                  book_red_mat),
                 ("DeskBook_2", 0.76, 0.88, 0.815, 0.10, 0.075, 0.025, -0.08,
                  book_teal_mat),
                 ("DeskBook_3", 0.74, 0.87, 0.855, 0.09, 0.07, 0.022, 0.04,
                  book_yellow_mat)]
    for (_bn, _bx, _by, _bz, _w, _d, _h, _rot, _mm) in book_defs:
        b = addToDesk(create_cube(_bn, (_bx, _by, _bz), (_w, _d, _h),
                                  material=_mm, bevel_width=0.004))
        b.rotation_euler[2] = _rot
        pages = addToDesk(create_cube("%s_Pages" % _bn, (_bx, _by, _bz),
                                      (_w * 0.94, _d * 0.96, _h * 0.62),
                                      material=pages_mat, bevel_width=0.002))
        pages.rotation_euler[2] = _rot
        spine = addToDesk(create_cube("%s_Spine" % _bn, (_bx, _by, _bz),
                                      (_w * 0.10, _d * 1.005, _h * 1.02),
                                      material=_mm, bevel_width=0.002))
        spine.rotation_euler[2] = _rot
        band = addToDesk(create_cube("%s_Band" % _bn, (_bx, _by, _bz + 0.002),
                                     (_w * 0.30, _d * 1.006, _h * 0.35),
                                     material=pages_mat, bevel_width=0.0))
        band.rotation_euler[2] = _rot
        # bookmark ribbon peeking out (same book)
        ribbon = addToDesk(create_cube("%s_Ribbon" % _bn,
                                       (_bx + 0.02, _by - _d * 0.45,
                                        _bz - _h * 0.4),
                                       (0.012, 0.03, 0.002),
                                       material=purple_blanket_mat,
                                       bevel_width=0.0))
        ribbon.rotation_euler[2] = _rot

    # mug (same cup: outer + inner + coffee + ring handle)
    addToDesk(create_cylinder("DeskMug", (0.86, 0.55, 0.77), radius=0.026,
                              depth=0.052, material=plant_pot_mat))
    addToDesk(create_cylinder("DeskMug_Inner", (0.86, 0.55, 0.782),
                              radius=0.021, depth=0.030, material=gap_mat,
                              end_fill='NOTHING'))
    addToDesk(create_cylinder("DeskMug_Coffee", (0.86, 0.55, 0.776),
                              radius=0.020, depth=0.004, material=coffee_mat))
    addToDesk(create_cylinder("DeskMug_BaseRing", (0.86, 0.55, 0.7455),
                              radius=0.020, depth=0.003,
                              material=white_plastic_mat))
    addToDesk(create_cylinder("DeskMug_Handle", (0.84, 0.55, 0.77),
                              radius=0.011, depth=0.01,
                              rotation=(1.5708, 0, 0),
                              material=plant_pot_mat))
    addToDesk(create_torus("DeskMug_HandleRing", (0.828, 0.55, 0.77),
                           0.013, 0.0035, (0, 1.5708, 0), plant_pot_mat))
    addToDesk(create_cube("DeskMug_Coaster", (0.86, 0.55, 0.7445),
                          (0.045, 0.045, 0.002), material=wood_mat,
                          bevel_width=0.001))

    # pen holder (same cup + same 2 pens, dressed)
    addToDesk(create_cylinder("PenHolder", (1.28, 0.55, 0.78), radius=0.024,
                              depth=0.06, material=black_plastic_mat))
    addToDesk(create_cylinder("PenHolder_Inner", (1.28, 0.55, 0.806),
                              radius=0.019, depth=0.006, material=gap_mat))
    addToDesk(create_torus("PenHolder_Rim", (1.28, 0.55, 0.810),
                           0.022, 0.0025, (0, 0, 0), grey_plastic_mat))
    p_blue_mat = create_simple_material("PenBlueMat", (0.10, 0.40, 0.80, 1.0),
                                        roughness=0.5, bump_scale=40.0,
                                        bump_strength=0.05)
    p_red_mat = create_simple_material("PenRedMat", (0.80, 0.10, 0.20, 1.0),
                                       roughness=0.5, bump_scale=40.0,
                                       bump_strength=0.05)
    p1_obj = create_cylinder("Pen_1", (1.27, 0.54, 0.83), radius=0.004,
                             depth=0.10, rotation=(0.2, 0.1, 0.2),
                             material=p_blue_mat)
    p2_obj = create_cylinder("Pen_2", (1.29, 0.56, 0.83), radius=0.004,
                             depth=0.10, rotation=(-0.25, -0.15, -0.1),
                             material=p_red_mat)
    addToDesk(p1_obj)
    addToDesk(p2_obj)
    addToDesk(create_cube("Pen_1_Clip", (1.272, 0.545, 0.855),
                          (0.002, 0.003, 0.030), material=dark_metal_mat,
                          bevel_width=0.0))
    addToDesk(create_cube("Pen_2_Clip", (1.292, 0.565, 0.855),
                          (0.002, 0.003, 0.030), material=dark_metal_mat,
                          bevel_width=0.0))
    addToDesk(create_cylinder("Pen_1_Tip", (1.265, 0.535, 0.782),
                              radius=0.002, depth=0.012,
                              rotation=(0.2, 0.1, 0.2), material=metal_mat))
    addToDesk(create_cylinder("Pen_2_Tip", (1.295, 0.565, 0.782),
                              radius=0.002, depth=0.012,
                              rotation=(-0.25, -0.15, -0.1), material=metal_mat))
    addToDesk(create_cylinder("Pen_1_Grip", (1.268, 0.538, 0.80),
                              radius=0.0048, depth=0.018,
                              rotation=(0.2, 0.1, 0.2), material=gap_mat))
    addToDesk(create_cylinder("Pen_2_Grip", (1.292, 0.562, 0.80),
                              radius=0.0048, depth=0.018,
                              rotation=(-0.25, -0.15, -0.1), material=gap_mat))

    # bucket (same red bucket, world-space)
    create_hollow_bucket("RedBucket", (-0.1, 1.4, 0.15), radius=0.14,
                         depth=0.28, material=red_bucket_mat,
                         rib_mat=red_bucket_mat)

    # LED strip (same back-wall strip: channel + diffuser + diodes)
    create_cube("LEDStrip_Channel", (0.0, 1.985, 0.04), (1.0, 0.012, 0.012),
                material=grey_plastic_mat, bevel_width=0.002)
    create_cube("LEDStrip_Diffuser", (0.0, 1.978, 0.04), (1.0, 0.004, 0.008),
                material=white_plastic_mat, bevel_width=0.001)
    create_cylinder("LEDStrip_BackWall", (0.0, 1.98, 0.04), radius=0.005,
                    depth=2.0, rotation=(0, 1.5708, 0), material=pink_led_mat)
    for i in range(24):
        _lx = -0.92 + i * 0.08
        _lm = pink_led_mat if i % 3 else strong_white_led_mat
        create_cube("LEDStrip_Diode_%02d" % i, (_lx, 1.976, 0.04),
                    (0.018, 0.004, 0.006), material=_lm, bevel_width=0.0)
    create_cube("LEDStrip_EndCap_L", (-1.0, 1.985, 0.04),
                (0.015, 0.014, 0.014), material=black_plastic_mat,
                bevel_width=0.002)
    create_cube("LEDStrip_EndCap_R", (1.0, 1.985, 0.04),
                (0.015, 0.014, 0.014), material=black_plastic_mat,
                bevel_width=0.002)

    desk_parent.rotation_euler[2] = -1.5708

    # ---------------------------------------------------------------- camera
    camera_data = bpy.data.cameras.new(name="IsometricCamera")
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 5.2
    camera_obj = bpy.data.objects.new("IsometricCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    bpy.context.scene.camera = camera_obj
    camera_obj.location = (8.5, -8.5, 8.5)
    camera_obj.rotation_euler = (0.955324, 0.0, 0.785398)
    try:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_perspective = 'CAMERA'
                        space.shading.type = 'RENDERED'
    except Exception:
        pass

    # ---------------------------------------------------------------- lights
    light_data_win = bpy.data.lights.new(name="WindowLight", type='AREA')
    light_data_win.energy = 220
    light_data_win.color = (0.4, 0.6, 1.0)
    light_data_win.size = 2.5
    light_win = bpy.data.objects.new("WindowLight", light_data_win)
    bpy.context.scene.collection.objects.link(light_win)
    light_win.location = (-2.5, -0.5, 1.55)
    light_win.rotation_euler = (0.0, 1.5708, 0.0)
    light_data_lamp = bpy.data.lights.new(name="LampLight", type='POINT')
    light_data_lamp.energy = 110
    light_data_lamp.color = (1.0, 0.9, 0.75)
    light_lamp = bpy.data.objects.new("LampLight", light_data_lamp)
    bpy.context.scene.collection.objects.link(light_lamp)
    light_lamp.location = (1.32, 0.85, 1.04)
    try:
        light_lamp.parent = desk_parent
        light_lamp.matrix_parent_inverse = desk_parent.matrix_world.inverted()
    except Exception:
        pass
    light_data_bed = bpy.data.lights.new(name="BedGlow", type='POINT')
    light_data_bed.energy = 20
    light_data_bed.color = (1.0, 0.0, 0.4)
    light_bed = bpy.data.objects.new("BedGlow", light_data_bed)
    bpy.context.scene.collection.objects.link(light_bed)
    light_bed.location = (-1.25, -0.35, 0.12)
    ceiling_bulb_mat = create_simple_material(
        "CeilingBulbMat", (1.0, 0.95, 0.80, 1.0), roughness=0.05,
        emission=(1.0, 0.92, 0.65, 1.0), emission_strength=15.0)
    wire_mat = create_simple_material("WireMat", (0.10, 0.10, 0.10, 1.0),
                                      roughness=0.9)
    # pendant socket assembly (same ceiling light, dressed)
    create_cylinder("Ceiling_Canopy", (-1.5, -0.5, 2.94), radius=0.025,
                    depth=0.02, material=white_plastic_mat)
    create_cylinder("Ceiling_Wire", (-1.5, -0.5, 2.85), radius=0.005,
                    depth=0.12, material=wire_mat)
    create_cylinder("Ceiling_WireClip", (-1.5, -0.5, 2.89), radius=0.008,
                    depth=0.012, material=dark_metal_mat)
    create_cylinder("Ceiling_Socket", (-1.5, -0.5, 2.76), radius=0.018,
                    depth=0.035, material=white_plastic_mat,
                    bevel_width=0.003)
    create_cylinder("Ceiling_SocketRing", (-1.5, -0.5, 2.745), radius=0.019,
                    depth=0.006, material=metal_mat)
    create_cylinder("Ceiling_Bulb", (-1.5, -0.5, 2.70), radius=0.032,
                    depth=0.05, material=ceiling_bulb_mat)
    create_sphere("Ceiling_BulbGlass", (-1.5, -0.5, 2.672), 0.030,
                  material=ceiling_bulb_mat)
    create_cylinder("Ceiling_Filament", (-1.5, -0.5, 2.672), radius=0.005,
                    depth=0.014, material=ceiling_bulb_mat)
    light_data_ceil = bpy.data.lights.new(name="CeilingBulbLight", type='POINT')
    light_data_ceil.energy = 180
    light_data_ceil.color = (1.0, 0.9, 0.68)
    try:
        light_data_ceil.shadow_soft_size = 0.08
    except Exception:
        pass
    light_ceil = bpy.data.objects.new("CeilingBulbLight", light_data_ceil)
    bpy.context.scene.collection.objects.link(light_ceil)
    light_ceil.location = (-1.5, -0.5, 2.66)
    light_data_fill = bpy.data.lights.new(name="AmbientFill", type='AREA')
    light_data_fill.energy = 8.0
    light_data_fill.color = (0.9, 0.92, 1.0)
    light_data_fill.size = 5.0
    light_fill = bpy.data.objects.new("AmbientFill", light_data_fill)
    bpy.context.scene.collection.objects.link(light_fill)
    light_fill.location = (0.0, 0.0, 4.5)
    light_fill.rotation_euler = (3.14159, 0.0, 0.0)

    # -------------------------------------------------------- render config
    bpy.context.scene.render.engine = 'CYCLES'
    try:
        bpy.context.scene.cycles.use_denoising = True
        bpy.context.scene.cycles.samples = 96
        bpy.context.scene.cycles.preview_samples = 256
    except Exception:
        pass
    if hasattr(bpy.context, "view_layer") and hasattr(bpy.context.view_layer,
                                                      "cycles"):
        try:
            bpy.context.view_layer.cycles.use_denoising = True
        except Exception:
            pass
    try:
        if hasattr(bpy.context.scene.cycles, "device"):
            bpy.context.scene.cycles.device = 'GPU'
    except Exception:
        pass
    try:
        bpy.context.scene.view_settings.view_transform = 'Standard'
    except TypeError:
        pass
    try:
        bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    except TypeError:
        try:
            bpy.context.scene.view_settings.look = 'High Contrast'
        except TypeError:
            pass
    try:
        if bpy.data.worlds.get("World"):
            world = bpy.data.worlds["World"]
            world.use_nodes = True
            bg_node = world.node_tree.nodes.get("Background")
            if bg_node:
                bg_node.inputs['Color'].default_value = (0.04, 0.04, 0.05, 1.0)
                bg_node.inputs['Strength'].default_value = 1.0
    except Exception:
        pass

    base_dir, public_dir = _export_paths()
    try:
        print("Baking procedural walnut wood texture...")
        bake_wood_texture(base_dir)
    except Exception as e:
        print("Failed to bake wood texture: %s" % e)
    glb_path = os.path.join(base_dir, "room_model.glb")
    fbx_path = os.path.join(base_dir, "room_model.fbx")
    try:
        bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB',
                                  use_selection=False, export_lights=True,
                                  export_cameras=True,
                                  export_materials='EXPORT')
        print("Exported GLB to: %s" % glb_path)
    except Exception as e:
        print("Failed to export GLB: %s" % e)
    try:
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=False,
                                 path_mode='COPY', embed_textures=True,
                                 object_types={'MESH', 'LIGHT', 'CAMERA'})
        print("Exported FBX to: %s" % fbx_path)
    except Exception as e:
        print("Failed to export FBX: %s" % e)
    try:
        print("Starting complete scene light baking for Three.js...")
        bake_and_export_combined_glb(public_dir)
    except Exception as e:
        print("Failed to bake and export combined GLB: %s" % e)
    render_path = os.path.join(base_dir, "room_render.png")
    bpy.context.scene.render.filepath = render_path
    try:
        oeng = bpy.context.scene.render.engine
    except Exception:
        oeng = 'CYCLES'
    try:
        osamp = bpy.context.scene.cycles.samples
    except Exception:
        osamp = 96
    bpy.context.scene.render.engine = 'CYCLES'
    try:
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.use_denoising = True
    except Exception:
        pass
    try:
        print("Rendering high-quality image of the room...")
        bpy.ops.render.render(write_still=True)
        print("Rendered image saved to: %s" % render_path)
    except Exception as e:
        print("Failed to render image: %s" % e)
    bpy.context.scene.render.engine = oeng
    try:
        bpy.context.scene.cycles.samples = osamp
    except Exception:
        pass
    print("Isometric room generation, texture baking, and export complete!")


if __name__ == "__main__":
    build_room()
