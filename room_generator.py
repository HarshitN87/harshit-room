import bpy
import math
import random

def clear_scene():
    """Unhides, unlocks, and deletes all objects in the scene to start with a blank slate."""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False
        
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Remove unused data blocks
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)

def apply_transforms(obj):
    """Applies scale and rotation to a mesh object, resetting scale to (1,1,1) for bevel accuracy."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def add_bevel_modifier(obj, width=0.02, segments=3):
    """Applies a smooth bevel modifier to make the low-poly models feel soft and stylized."""
    modifier = obj.modifiers.new(name="Bevel", type='BEVEL')
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = 'ANGLE'
    modifier.angle_limit = 0.523599 # ~30 degrees in radians

def enable_smooth_shading(obj, angle=0.523599):
    """Applies smooth shading and configures Auto-Smooth/Smooth by Angle in a version-safe manner."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # In Blender 4.2+ and 5.x, shade_auto_smooth operator adds the nodes-based modifier automatically
    if hasattr(bpy.ops.object, "shade_auto_smooth"):
        bpy.ops.object.shade_auto_smooth()
        if "Smooth by Angle" in obj.modifiers:
            mod = obj.modifiers["Smooth by Angle"]
            try:
                mod["Input_1"] = angle # Set angle in radians
            except Exception:
                pass
    # In Blender pre-4.1, legacy auto smooth properties exist
    elif hasattr(obj.data, 'use_auto_smooth'):
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = angle
    # Fallback to standard smooth shading
    else:
        bpy.ops.object.shade_smooth()

def create_cube(name, location, scale, material=None, bevel_width=0.01):
    """Creates a cube, scales it, applies transforms, enables smooth shading, and adds optional bevel & material."""
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    apply_transforms(obj)
    
    if bevel_width > 0:
        add_bevel_modifier(obj, width=bevel_width)
        
    enable_smooth_shading(obj)
    
    if material:
        obj.data.materials.append(material)
        
    return obj

def create_cylinder(name, location, radius, depth, rotation=(0,0,0), material=None, bevel_width=0.0):
    """Creates a cylinder, sets scale/rotation, applies transforms, enables smooth shading, and adds optional bevel & material."""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    apply_transforms(obj)
    
    if bevel_width > 0:
        add_bevel_modifier(obj, width=bevel_width)
        
    enable_smooth_shading(obj)
    
    if material:
        obj.data.materials.append(material)
        
    return obj

def create_hollow_bucket(name, location, radius, depth, material):
    """Creates a hollow dustbin with thickness (using a Solidify modifier) and adds a bottom cap."""
    # Cylinder with open ends
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, end_fill_type='NOTHING', location=location)
    obj = bpy.context.active_object
    obj.name = name
    
    # Add solidify modifier for wall thickness
    solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 0.012
    
    # Bevel and smooth shading
    add_bevel_modifier(obj, width=0.003)
    enable_smooth_shading(obj)
    
    # Bottom cap (flat thin cylinder at the base)
    bpy.ops.mesh.primitive_cylinder_add(radius=radius - 0.006, depth=0.01, location=(location[0], location[1], location[2] - depth/2.0 + 0.005))
    bottom = bpy.context.active_object
    bottom.name = f"{name}_Bottom"
    enable_smooth_shading(bottom)
    
    # Parent bottom to main bucket
    bottom.parent = obj
    bottom.matrix_parent_inverse = obj.matrix_world.inverted()
    
    if material:
        obj.data.materials.append(material)
        bottom.data.materials.append(material)
        
    return obj

def set_principled_inputs(principled, inputs_dict):
    """Sets socket inputs on a Principled BSDF node, supporting both Blender 3.x and 4.x/5.x formats."""
    for key, val in inputs_dict.items():
        if key in principled.inputs:
            principled.inputs[key].default_value = val
        elif key == 'Emission Color' and 'Emission' in principled.inputs:
            principled.inputs['Emission'].default_value = val

def create_simple_material(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=1.0):
    """Creates a basic material with optional emission (glow)."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = color  # Sets viewport color so Solid view mode matches the nodes
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        inputs = {
            'Base Color': color,
            'Roughness': roughness,
            'Metallic': metallic
        }
        if emission:
            inputs['Emission Color'] = emission
            inputs['Emission Strength'] = emission_strength
        set_principled_inputs(principled, inputs)
    return mat

def create_bedsheet_material():
    """Generates a cozy solid slate blue bedsheet material."""
    return create_simple_material("BedsheetMat", (0.35, 0.45, 0.52, 1.0), roughness=0.85)

def create_wood_material():
    """Generates an elegant warm walnut wood material with wave-based wood grain matching the reference."""
    mat = bpy.data.materials.new(name="WarmWood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    principled = nodes.get("Principled BSDF")
    if not principled:
        return mat
        
    for link in principled.inputs['Base Color'].links:
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
    
    colorramp = nodes.new(type="ShaderNodeValToRGB")
    stops = colorramp.color_ramp.elements
    stops[0].color = (0.42, 0.24, 0.14, 1.0) # Elegant dark walnut grain
    stops[0].position = 0.0
    stops[1].color = (0.62, 0.40, 0.26, 1.0) # Warm medium-brown wood
    stops[1].position = 1.0
    
    links.new(wave.outputs['Color'], colorramp.inputs['Fac'])
    links.new(colorramp.outputs['Color'], principled.inputs['Base Color'])
    principled.inputs['Roughness'].default_value = 0.25
    return mat

def create_floor_planks():
    """Creates a stylized geometric starburst parquet tile floor matching the user's photos."""
    # Matte wood colors with high roughness (0.95) to prevent reflections/shine
    floor_cream = create_simple_material("FloorCream", (0.62, 0.48, 0.36, 1.0), roughness=0.95)
    floor_tan = create_simple_material("FloorTan", (0.68, 0.54, 0.42, 1.0), roughness=0.95)
    floor_brown = create_simple_material("FloorBrown", (0.50, 0.35, 0.24, 1.0), roughness=0.95)
    floor_dark = create_simple_material("FloorDark", (0.32, 0.22, 0.16, 1.0), roughness=0.95)

    # 5x5 grid of square tiles, each 0.8m x 0.8m covering the 4m x 4m room floor
    random.seed(105)
    for ix in range(5):
        tx = -1.6 + ix * 0.8
        for iy in range(5):
            ty = -1.6 + iy * 0.8
            
            # 1. Base Tile (Square border)
            create_cube(f"TileBase_{ix}_{iy}", (tx, ty, -0.01), (0.395, 0.395, 0.005), material=floor_brown, bevel_width=0.001)
            
            # 2. Outer Diamond (rotated by 45 deg)
            diamond = create_cube(f"TileDiamond_{ix}_{iy}", (tx, ty, -0.008), (0.24, 0.24, 0.005), material=floor_cream, bevel_width=0.001)
            diamond.rotation_euler[2] = 0.785398  # 45 degrees
            
            # 3. Inner Center Square (unrotated)
            create_cube(f"TileCenter_{ix}_{iy}", (tx, ty, -0.006), (0.12, 0.12, 0.005), material=floor_tan, bevel_width=0.001)
            
            # 4. Starburst/Pinwheel Spoke Pattern (4 thin crossing planks rotated by 0, 45, 90, 135 deg)
            for s in range(4):
                angle = s * math.pi / 4
                spoke = create_cube(f"TileSpoke_{ix}_{iy}_{s}", (tx, ty, -0.004), (0.11, 0.015, 0.005), material=floor_dark, bevel_width=0.0005)
                spoke.rotation_euler[2] = angle

def bake_wood_texture():
    """Bakes the procedural wood grain into a 2D image texture and applies it to WarmWood,
    ensuring it exports correctly with its wood grain pattern in GLB/FBX."""
    import os
    
    mat = bpy.data.materials.get("WarmWood")
    if not mat:
        return
        
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 1. Create target image
    export_dir = r"C:\Users\negih\Downloads\grok_try_resume"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    img_path = os.path.join(export_dir, "wood_baked.png")
    
    # Create image block
    img = bpy.data.images.new("WarmWoodBaked", 1024, 1024)
    img.filepath_raw = img_path
    img.file_format = 'PNG'
    
    # 2. Add and setup image texture node (must be active for baking)
    tex_node = nodes.new(type="ShaderNodeTexImage")
    tex_node.image = img
    nodes.active = tex_node
    
    # 3. Create a temporary plane for baking
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -10))
    plane = bpy.context.active_object
    plane.name = "TempBakePlane"
    plane.data.materials.append(mat)
    
    # Ensure it's UV unwrapped
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Select only the plane
    bpy.ops.object.select_all(action='DESELECT')
    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    
    # Save original render settings
    orig_engine = bpy.context.scene.render.engine
    orig_samples = bpy.context.scene.cycles.samples
    orig_device = bpy.context.scene.cycles.device
    
    # Setup Cycles for instant bake (1 sample is enough for constant flat emission)
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 1
    
    # Connect colorramp directly to a temporary Emission node to bake color values flat
    colorramp = None
    for n in nodes:
        if n.type == 'VALTORGB':
            colorramp = n
            break
            
    principled = nodes.get("Principled BSDF")
    
    if colorramp and principled:
        # Create temporary emission
        emit_node = nodes.new(type="ShaderNodeEmission")
        links.new(colorramp.outputs['Color'], emit_node.inputs['Color'])
        
        # Link emission to surface output
        output_node = None
        for n in nodes:
            if n.type == 'OUTPUT_MATERIAL':
                output_node = n
                break
                
        if output_node:
            orig_link = output_node.inputs['Surface'].links[0].from_socket if output_node.inputs['Surface'].links else None
            links.new(emit_node.outputs['Emission'], output_node.inputs['Surface'])
            
            # Bake
            bpy.ops.object.bake(type='EMIT')
            
            # Save image
            img.save()
            
            # Restore original link and cleanup temporary nodes
            if orig_link:
                links.new(orig_link, output_node.inputs['Surface'])
            nodes.remove(emit_node)
            
    # Connect baked image texture node to Principled BSDF Base Color
    if principled:
        for link in principled.inputs['Base Color'].links:
            links.remove(link)
        links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
        
    # Restore original settings
    bpy.context.scene.render.engine = orig_engine
    bpy.context.scene.cycles.samples = orig_samples
    bpy.context.scene.cycles.device = orig_device
    
    # Remove temporary plane
    bpy.data.objects.remove(plane, do_unlink=True)

def bake_and_export_combined_glb():
    """Bakes the complete Cycles path-traced lighting (colors, shadows, LED glows) of the entire room
    into a single merged mesh with a single 2048x2048 texture sheet. This creates a fully-baked
    unlit GLB model that looks exactly like the Cycles render in real-time WebGL (like Three.js)."""
    import os
    
    # Save original selection
    original_selection = [obj for obj in bpy.context.selected_objects]
    original_active = bpy.context.view_layer.objects.active
    
    # 1. Select all mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    mesh_objs = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            mesh_objs.append(obj)
            
    if not mesh_objs:
        print("No meshes found to bake!")
        return
        
    # 2. Duplicate them to avoid modifying original editable objects
    bpy.ops.object.duplicate()
    dup_objs = [obj for obj in bpy.context.selected_objects]
    
    # Hide original meshes from render to prevent overlap shadow artifacts during bake
    for obj in mesh_objs:
        obj.hide_render = True
        
    # Join duplicate objects into a single mesh
    bpy.context.view_layer.objects.active = dup_objs[0]
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    merged_obj.name = "Baked_Room_Mesh"
    
    # 3. Smart UV Project to unwrap the entire room onto one UV sheet
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.015)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 4. Create the target image texture
    export_dir = r"C:\Users\negih\Downloads\grok_try_resume\public"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    img_path = os.path.join(export_dir, "room_baked_combined.png")
    
    # Create a 4096x4096 texture image for ultimate WebGL sharpness
    img = bpy.data.images.new("RoomBakedCombined", 4096, 4096)
    img.filepath_raw = img_path
    img.file_format = 'PNG'
    
    # 5. Add and make this image node active on every single material in the scene
    added_nodes = []
    for mat in bpy.data.materials:
        if mat.use_nodes:
            tex_node = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
            tex_node.image = img
            mat.node_tree.nodes.active = tex_node
            added_nodes.append((mat, tex_node))
            
    # 6. Save current render settings
    orig_engine = bpy.context.scene.render.engine
    orig_samples = bpy.context.scene.cycles.samples
    orig_device = bpy.context.scene.cycles.device
    
    # Configure Cycles for combined bake
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64  # Balanced quality and fast baking
    
    # Run Combined Bake (bakes diffuse, shadows, emissive glows)
    print("Baking combined lighting (this might take a few seconds)...")
    bpy.ops.object.bake(type='COMBINED')
    
    # Save the baked image
    img.save()
    
    # 7. Create a clean unlit material for the exported model
    baked_mat = bpy.data.materials.new(name="BakedRoomMaterial")
    baked_mat.use_nodes = True
    nodes = baked_mat.node_tree.nodes
    links = baked_mat.node_tree.links
    
    # Remove Principled BSDF and use Emission (unlit) so lighting is 100% constant in WebGL
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
        
    # Clear old material slots and assign only the baked material
    merged_obj.data.materials.clear()
    merged_obj.data.materials.append(baked_mat)
    
    # 8. Export the merged baked model
    baked_glb_path = os.path.join(export_dir, "room_baked_combined.glb")
    
    # Select only the merged baked object for export
    bpy.ops.object.select_all(action='DESELECT')
    merged_obj.select_set(True)
    bpy.context.view_layer.objects.active = merged_obj
    
    try:
        bpy.ops.export_scene.gltf(
            filepath=baked_glb_path,
            export_format='GLB',
            use_selection=True,
            export_materials='EXPORT'
        )
        print(f"Exported baked combined GLB to: {baked_glb_path}")
    except Exception as e:
        print(f"Failed to export baked GLB: {e}")
        
    # 9. Cleanup
    # Delete duplicate baked mesh
    bpy.data.objects.remove(merged_obj, do_unlink=True)
    
    # Remove baked texture nodes from original materials
    for mat, node in added_nodes:
        try:
            mat.node_tree.nodes.remove(node)
        except Exception:
            pass
            
    # Restore original meshes render visibility
    for obj in mesh_objs:
        obj.hide_render = False
        
    # Restore original settings
    bpy.context.scene.render.engine = orig_engine
    bpy.context.scene.cycles.samples = orig_samples
    bpy.context.scene.cycles.device = orig_device
    
    # Restore original selection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selection:
        obj.select_set(True)
    if original_active:
        bpy.context.view_layer.objects.active = original_active

def build_room():
    # 1. Clear scene
    clear_scene()
    
    # 2. Set up materials
    bedsheet_mat = create_bedsheet_material()
    wood_mat = create_wood_material()
    
    # Single off-white material for both walls to ensure they look identical
    wall_mat = create_simple_material("WallMat", (0.92, 0.90, 0.87, 1.0), roughness=0.85)
    
    baseboard_mat = create_simple_material("BaseboardMat", (0.95, 0.95, 0.95, 1.0), roughness=0.2)
    window_frame_mat = create_simple_material("WindowFrameMat", (0.96, 0.96, 0.96, 1.0), roughness=0.2)
    glass_mat = create_simple_material("GlassMat", (0.5, 0.8, 0.95, 1.0), roughness=0.1, emission=(0.1, 0.2, 0.3, 1.0), emission_strength=0.5)
    metal_mat = create_simple_material("MetalMat", (0.85, 0.85, 0.85, 1.0), roughness=0.15, metallic=1.0)
    
    black_plastic_mat = create_simple_material("BlackPlasticMat", (0.07, 0.07, 0.07, 1.0), roughness=0.45)
    grey_plastic_mat = create_simple_material("GreyPlasticMat", (0.28, 0.28, 0.28, 1.0), roughness=0.5)
    white_plastic_mat = create_simple_material("WhitePlasticMat", (0.93, 0.93, 0.93, 1.0), roughness=0.3)
    
    pink_curtain_mat = create_simple_material("PinkCurtainMat", (0.92, 0.52, 0.62, 1.0), roughness=0.85)
    teal_curtain_mat = create_simple_material("TealCurtainMat", (0.18, 0.58, 0.63, 1.0), roughness=0.85)
    red_bucket_mat = create_simple_material("RedBucketMat", (0.85, 0.12, 0.12, 1.0), roughness=0.35)
    
    # Saturated colorful blankets/pillows
    slate_pillow_mat = create_simple_material("SlatePillowMat", (0.42, 0.52, 0.60, 1.0), roughness=0.85)
    purple_blanket_mat = create_simple_material("PurpleBlanketMat", (0.35, 0.1, 0.55, 1.0), roughness=0.85)
    pink_blanket_mat = create_simple_material("PinkBlanketMat", (0.85, 0.1, 0.38, 1.0), roughness=0.85)
    
    # Glowing emitters
    screen_emit_mat = create_simple_material("ScreenEmitMat", (0.05, 0.1, 0.15, 1.0), roughness=0.1, emission=(0.3, 0.7, 1.0, 1.0), emission_strength=5.0)
    keyboard_emit_mat = create_simple_material("KeyboardEmitMat", (0.05, 0.1, 0.15, 1.0), roughness=0.1, emission=(0.2, 0.6, 1.0, 1.0), emission_strength=10.0)
    cyan_led_mat = create_simple_material("CyanLEDMat", (0.0, 1.0, 1.0, 1.0), roughness=0.2, emission=(0.0, 0.9, 1.0, 1.0), emission_strength=25.0)
    pink_led_mat = create_simple_material("PinkLEDMat", (1.0, 0.0, 0.3, 1.0), roughness=0.2, emission=(1.0, 0.0, 0.3, 1.0), emission_strength=25.0)
    strong_white_led_mat = create_simple_material("WhiteLEDMat", (1.0, 1.0, 0.9, 1.0), roughness=0.2, emission=(1.0, 1.0, 0.9, 1.0), emission_strength=20.0)
    
    bottle_mat = create_simple_material("BottleMat", (0.85, 0.8, 0.2, 1.0), roughness=0.2, metallic=0.0)
    
    # Book materials declared at the top for global function scope
    book_red_mat = create_simple_material("BookRedMat", (0.85, 0.15, 0.15, 1.0), roughness=0.8)
    book_teal_mat = create_simple_material("BookTealMat", (0.15, 0.65, 0.65, 1.0), roughness=0.8)
    book_yellow_mat = create_simple_material("BookYellowMat", (0.95, 0.75, 0.1, 1.0), roughness=0.8)
    
    # Plant materials
    plant_pot_mat = create_simple_material("PlantPotMat", (0.95, 0.95, 0.93, 1.0), roughness=0.3)
    plant_leaf_mat = create_simple_material("PlantLeafMat", (0.18, 0.48, 0.22, 1.0), roughness=0.8)
    plant_soil_mat = create_simple_material("PlantSoilMat", (0.28, 0.18, 0.12, 1.0), roughness=0.9)

    # 3. Create Wood Planks Floor
    create_floor_planks()
    
    # 4. Left Wall (X = -2.0) with Window Cutout
    create_cube("Wall_Left_Post1", (-2.025, -1.6, 1.5), (0.025, 0.4, 1.5), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_Post2", (-2.025, 1.1, 1.5), (0.025, 0.9, 1.5), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_UnderWindow", (-2.025, -0.5, 0.4), (0.025, 0.7, 0.4), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Left_AboveWindow", (-2.025, -0.5, 2.65), (0.025, 0.7, 0.35), material=wall_mat, bevel_width=0.0)
    
    # Baseboards (Moulding)
    create_cube("Baseboard_Left", (-1.99, 0.0, 0.04), (0.01, 2.0, 0.04), material=baseboard_mat, bevel_width=0.002)
    create_cube("Baseboard_Back_1", (-0.75, 1.99, 0.04), (1.25, 0.01, 0.04), material=baseboard_mat, bevel_width=0.002)
    create_cube("Baseboard_Back_2", (1.75, 1.99, 0.04), (0.25, 0.01, 0.04), material=baseboard_mat, bevel_width=0.002)

    # Window Frame & Glass panes
    create_cube("Window_Sill_Bottom", (-2.01, -0.5, 0.8), (0.02, 0.72, 0.015), material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Sill_Top", (-2.01, -0.5, 2.3), (0.02, 0.72, 0.015), material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Sill_Left", (-2.01, -1.2, 1.55), (0.02, 0.015, 0.75), material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Sill_Right", (-2.01, 0.2, 1.55), (0.02, 0.015, 0.75), material=window_frame_mat, bevel_width=0.005)
    create_cube("Window_Glass", (-2.01, -0.5, 1.55), (0.005, 0.7, 0.73), material=glass_mat, bevel_width=0.0)
    
    # 5. Back Wall (Y = 2.0) with Door Opening
    create_cube("Wall_Back_Post1", (-0.75, 2.025, 1.5), (1.25, 0.025, 1.5), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Back_Post2", (1.75, 2.025, 1.5), (0.25, 0.025, 1.5), material=wall_mat, bevel_width=0.0)
    create_cube("Wall_Back_AboveDoor", (1.0, 2.025, 2.6), (0.5, 0.025, 0.4), material=wall_mat, bevel_width=0.0)
    
    # Door Frame (White glossy frame)
    create_cube("DoorFrame_Left", (0.5, 2.01, 1.1), (0.015, 0.02, 1.1), material=window_frame_mat, bevel_width=0.005)
    create_cube("DoorFrame_Right", (1.5, 2.01, 1.1), (0.015, 0.02, 1.1), material=window_frame_mat, bevel_width=0.005)
    create_cube("DoorFrame_Top", (1.0, 2.01, 2.2), (0.515, 0.02, 0.015), material=window_frame_mat, bevel_width=0.005)
    
    # Door Panel (Hinged at X = 1.5, slightly open at -25 degrees)
    theta = -0.436
    door_w = 0.485
    door_th = 0.02
    door_h = 1.09
    dx = 1.5 - door_w * math.cos(theta)
    dy = 2.0 - door_w * math.sin(theta)
    door = create_cube("DoorPanel", (dx, dy, 1.1), (door_w, door_th, door_h), material=wood_mat, bevel_width=0.01)
    door.rotation_euler[2] = theta
    
    # Door Handle/Latch knob
    hx = 1.5 - 2 * door_w * math.cos(theta)
    hy = 2.0 - 2 * door_w * math.sin(theta)
    handle = create_cube("DoorHandle", (hx, hy - 0.03 * math.cos(theta), 1.0), (0.015, 0.04, 0.015), material=metal_mat, bevel_width=0.003)
    handle.rotation_euler[2] = theta
    
    # 6. Curtain Rods & Curtains
    create_cylinder("WindowCurtainRod", (-1.95, -0.5, 2.45), radius=0.015, depth=1.8, rotation=(1.5708, 0, 0), material=metal_mat)
    
    # 6b. Realistic Wavy Curtains
    def create_wavy_curtain(name, start_y, end_y, x_center, material):
        steps = 16
        y_step = (end_y - start_y) / steps
        for i in range(steps):
            y = start_y + i * y_step + y_step / 2.0
            # Sine wave ripple in X-direction to create accordion fold geometry
            x_offset = 0.02 * math.sin(i * 1.2)
            
            create_cube(f"{name}_Fold_{i}", 
                        (x_center + x_offset, y, 1.45), 
                        (0.015, y_step * 0.7, 0.95), 
                        material=material, 
                        bevel_width=0.003)
            
            # Add curtain loops/rings at the top (Z = 2.4) connecting to the rod
            if i % 2 == 0:
                create_cube(f"{name}_Loop_{i}",
                            (-1.94 + x_offset * 0.5, y, 2.43),
                            (0.02, 0.008, 0.03),
                            material=material,
                            bevel_width=0.001)

    create_wavy_curtain("PinkCurtain", -1.2, -0.7, -1.91, pink_curtain_mat)
    create_wavy_curtain("TealCurtain", -0.3, 0.2, -1.91, teal_curtain_mat)

    # 7. Wardrobe (Back wall, left side)
    # Carcass
    create_cube("Wardrobe_Body", (-1.0, 1.7, 1.3), (0.8, 0.25, 1.3), material=wood_mat, bevel_width=0.01)
    # Bottom Drawers
    create_cube("Wardrobe_Drawer_L", (-1.395, 1.44, 0.2), (0.38, 0.01, 0.12), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Drawer_L_Inset", (-1.395, 1.432, 0.2), (0.31, 0.004, 0.08), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Drawer_R", (-0.605, 1.44, 0.2), (0.38, 0.01, 0.12), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Drawer_R_Inset", (-0.605, 1.432, 0.2), (0.31, 0.004, 0.08), material=wood_mat, bevel_width=0.004)
    # Lower Door Panels
    create_cube("Wardrobe_Door_LL", (-1.395, 1.44, 1.075), (0.38, 0.01, 0.675), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_LL_Inset", (-1.395, 1.432, 1.075), (0.31, 0.004, 0.60), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Door_LR", (-0.605, 1.44, 1.075), (0.38, 0.01, 0.675), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_LR_Inset", (-0.605, 1.432, 1.075), (0.31, 0.004, 0.60), material=wood_mat, bevel_width=0.004)
    # Upper Door Panels
    create_cube("Wardrobe_Door_UL", (-1.395, 1.44, 2.2), (0.38, 0.01, 0.35), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_UL_Inset", (-1.395, 1.432, 2.2), (0.31, 0.004, 0.28), material=wood_mat, bevel_width=0.004)
    create_cube("Wardrobe_Door_UR", (-0.605, 1.44, 2.2), (0.38, 0.01, 0.35), material=wood_mat, bevel_width=0.008)
    create_cube("Wardrobe_Door_UR_Inset", (-0.605, 1.432, 2.2), (0.31, 0.004, 0.28), material=wood_mat, bevel_width=0.004)
    # Handles
    create_cube("Wardrobe_Handle_LL", (-1.05, 1.42, 1.0), (0.01, 0.01, 0.08), material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_LR", (-0.95, 1.42, 1.0), (0.01, 0.01, 0.08), material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_UL", (-1.2, 1.42, 1.95), (0.06, 0.01, 0.01), material=metal_mat, bevel_width=0.002)
    create_cube("Wardrobe_Handle_UR", (-0.8, 1.42, 1.95), (0.06, 0.01, 0.01), material=metal_mat, bevel_width=0.002)
    
    # Detailed Key in Right Door Lock (Z = 1.1)
    create_cylinder("Wardrobe_LockPlate", (-0.95, 1.425, 1.15), radius=0.008, depth=0.005, rotation=(1.5708, 0, 0), material=metal_mat)
    create_cylinder("Wardrobe_KeyShaft", (-0.95, 1.41, 1.15), radius=0.0018, depth=0.025, rotation=(1.5708, 0, 0), material=metal_mat)
    create_cylinder("Wardrobe_KeyHead", (-0.95, 1.395, 1.15), radius=0.006, depth=0.003, rotation=(1.5708, 0, 0), material=metal_mat)

    # 8. Bed & Bedding (Squarish double bed frame: 1.5m width x 1.8m length)
    create_cube("BedFrame_SideR", (-0.49, -0.3, 0.175), (0.02, 0.9, 0.175), material=wood_mat, bevel_width=0.01)
    create_cube("BedFrame_SideL", (-1.99, -0.3, 0.175), (0.02, 0.9, 0.175), material=wood_mat, bevel_width=0.01)
    create_cube("BedFrame_Front", (-1.24, -1.21, 0.175), (0.73, 0.02, 0.175), material=wood_mat, bevel_width=0.01)
    create_cube("BedFrame_Headboard", (-1.24, 0.61, 0.3), (0.73, 0.02, 0.3), material=wood_mat, bevel_width=0.01)
    
    # Mattress
    create_cube("Mattress", (-1.24, -0.3, 0.36), (0.72, 0.88, 0.09), material=bedsheet_mat, bevel_width=0.02)
    # Pillows
    p1 = create_cube("Pillow_1", (-1.55, 0.35, 0.45), (0.24, 0.16, 0.035), material=slate_pillow_mat, bevel_width=0.015)
    p1.rotation_euler = (0.05, -0.05, 0.08)
    p2 = create_cube("Pillow_2", (-0.93, 0.35, 0.45), (0.24, 0.16, 0.035), material=slate_pillow_mat, bevel_width=0.015)
    p2.rotation_euler = (0.05, 0.05, -0.08)
    # Draped blankets
    create_cube("Blanket_Purple_Top", (-1.24, -0.2, 0.42), (0.72, 0.6, 0.02), material=purple_blanket_mat, bevel_width=0.015)
    create_cube("Blanket_Purple_Drape", (-0.51, -0.2, 0.285), (0.01, 0.6, 0.135), material=purple_blanket_mat, bevel_width=0.015)



    # 9. Study Desk (Original 1.2m width, shifted to the right to X = 1.4, slimmed depth to 0.5m)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.4, 0.7, 0.0))
    desk_parent = bpy.context.active_object
    desk_parent.name = "Desk_Group"

    def addToDesk(obj):
        obj.parent = desk_parent
        obj.matrix_parent_inverse = desk_parent.matrix_world.inverted()
        return obj

    # Desktop (1.2m wide, 0.5m deep)
    addToDesk(create_cube("Desk_Top", (1.2, 0.7, 0.735), (0.6, 0.25, 0.015), material=wood_mat, bevel_width=0.008))
    
    # Left and Right solid wood side panels
    addToDesk(create_cube("Desk_Panel_Left", (0.61, 0.7, 0.36), (0.015, 0.23, 0.36), material=wood_mat, bevel_width=0.005))
    addToDesk(create_cube("Desk_Panel_Right", (1.79, 0.7, 0.36), (0.015, 0.23, 0.36), material=wood_mat, bevel_width=0.005))
    
    # Modesty Panel (Back board)
    addToDesk(create_cube("Desk_Modesty_Back", (1.03, 0.915, 0.51), (0.4, 0.015, 0.21), material=wood_mat, bevel_width=0.003))
    
    # Slidable Keyboard Tray
    addToDesk(create_cube("Desk_Keyboard_Tray", (1.03, 0.65, 0.66), (0.35, 0.18, 0.01), material=wood_mat, bevel_width=0.003))
    
    # Horizontal Footrest Shelf at the bottom of legroom
    addToDesk(create_cube("Desk_Footrest_Shelf", (1.03, 0.7, 0.11), (0.4, 0.18, 0.01), material=wood_mat, bevel_width=0.003))
    # Front riser board below footrest shelf
    addToDesk(create_cube("Desk_Footrest_Riser", (1.03, 0.52, 0.05), (0.4, 0.01, 0.05), material=wood_mat, bevel_width=0.003))

    # Right-side Cabinet/Drawers Box Casing (slimmed drawer casing width)
    addToDesk(create_cube("Desk_Drawers_Box", (1.6, 0.7, 0.36), (0.16, 0.23, 0.36), material=wood_mat, bevel_width=0.005))
    # Top Drawer (Horizontal handle, key lock on the right side)
    addToDesk(create_cube("Desk_Drawer_Top", (1.6, 0.475, 0.61), (0.155, 0.005, 0.08), material=wood_mat, bevel_width=0.004))
    addToDesk(create_cube("Desk_Drawer_Handle_Top", (1.6, 0.465, 0.61), (0.04, 0.005, 0.006), material=metal_mat, bevel_width=0.002))
    addToDesk(create_cylinder("Desk_Drawer_Lock", (1.71, 0.47, 0.66), radius=0.005, depth=0.005, rotation=(1.5708, 0, 0), material=metal_mat))
    # Bottom Cabinet Door (Vertical handle on the left side)
    addToDesk(create_cube("Desk_Cabinet_Door", (1.6, 0.475, 0.265), (0.155, 0.005, 0.22), material=wood_mat, bevel_width=0.004))
    addToDesk(create_cube("Desk_Cabinet_Handle", (1.46, 0.465, 0.265), (0.006, 0.005, 0.05), material=metal_mat, bevel_width=0.002))

    # 10. Office Mesh Chair (Centered to face the legroom cavity, shifted X by 0.2m)
    # Hub & cylinder
    create_cube("Chair_Hub", (0.55, 0.95, 0.08), (0.04, 0.04, 0.02), material=black_plastic_mat, bevel_width=0.005)
    for i in range(5):
        angle = i * 2 * math.pi / 5
        lx = 0.55 + 0.22 * math.cos(angle)
        ly = 0.95 + 0.22 * math.sin(angle)
        leg = create_cube(f"Chair_Leg_{i}", (lx, ly, 0.08), (0.11, 0.02, 0.015), material=black_plastic_mat, bevel_width=0.004)
        leg.rotation_euler[2] = angle
        
        # Double wheels
        wx1 = 0.55 + 0.28 * math.cos(angle) - 0.015 * math.sin(angle)
        wy1 = 0.95 + 0.28 * math.sin(angle) + 0.015 * math.cos(angle)
        create_cylinder(f"Chair_Wheel_A_{i}", (wx1, wy1, 0.04), radius=0.03, depth=0.015, rotation=(1.5708, 0, angle), material=black_plastic_mat)
        wx2 = 0.55 + 0.28 * math.cos(angle) + 0.015 * math.sin(angle)
        wy2 = 0.95 + 0.28 * math.sin(angle) - 0.015 * math.cos(angle)
        create_cylinder(f"Chair_Wheel_B_{i}", (wx2, wy2, 0.04), radius=0.03, depth=0.015, rotation=(1.5708, 0, angle), material=black_plastic_mat)
        
    create_cylinder("Chair_Cylinder", (0.55, 0.95, 0.24), radius=0.025, depth=0.18, material=metal_mat)
    create_cylinder("Chair_Sheath", (0.55, 0.95, 0.16), radius=0.038, depth=0.08, material=black_plastic_mat)
    
    # Seat
    create_cube("Chair_Seat", (0.55, 0.95, 0.43), (0.22, 0.22, 0.035), material=black_plastic_mat, bevel_width=0.01)
    create_cube("Chair_Seat_BolsterL", (0.55, 1.16, 0.45), (0.22, 0.02, 0.02), material=black_plastic_mat, bevel_width=0.005)
    create_cube("Chair_Seat_BolsterR", (0.55, 0.74, 0.45), (0.22, 0.02, 0.02), material=black_plastic_mat, bevel_width=0.005)
    
    # Armrests
    create_cube("Chair_Arm_Left_Support", (0.55, 1.18, 0.53), (0.015, 0.015, 0.08), material=black_plastic_mat, bevel_width=0.002)
    create_cube("Chair_Arm_Left_Pad", (0.59, 1.18, 0.615), (0.1, 0.03, 0.015), material=black_plastic_mat, bevel_width=0.004)
    create_cube("Chair_Arm_Right_Support", (0.55, 0.72, 0.53), (0.015, 0.015, 0.08), material=black_plastic_mat, bevel_width=0.002)
    create_cube("Chair_Arm_Right_Pad", (0.59, 0.72, 0.615), (0.1, 0.03, 0.015), material=black_plastic_mat, bevel_width=0.004)
    
    # Mesh Backrest with border frame
    create_cube("Chair_Back_Support", (0.32, 0.95, 0.56), (0.015, 0.025, 0.15), material=black_plastic_mat, bevel_width=0.004)
    create_cube("Chair_Back_Frame_L", (0.34, 0.77, 0.75), (0.02, 0.015, 0.28), material=black_plastic_mat, bevel_width=0.006)
    create_cube("Chair_Back_Frame_R", (0.34, 1.13, 0.75), (0.02, 0.015, 0.28), material=black_plastic_mat, bevel_width=0.006)
    create_cube("Chair_Back_Frame_Top", (0.34, 0.95, 1.02), (0.02, 0.18, 0.015), material=black_plastic_mat, bevel_width=0.006)
    create_cube("Chair_Back_Frame_Bot", (0.34, 0.95, 0.48), (0.02, 0.18, 0.015), material=black_plastic_mat, bevel_width=0.006)
    create_cube("Chair_Back_Mesh", (0.345, 0.95, 0.75), (0.01, 0.17, 0.26), material=black_plastic_mat, bevel_width=0.0)
    create_cube("Chair_Headrest", (0.34, 0.95, 1.08), (0.02, 0.13, 0.06), material=black_plastic_mat, bevel_width=0.01)

    # 11. Props & Accessories (Repositioned to sit correctly on the 0.6m depth desk)
    # 11. Props & Accessories (Repositioned to sit correctly on the 0.6m depth desk)
    # Desk mat
    addToDesk(create_cube("DeskMat", (1.1, 0.68, 0.745), (0.2, 0.25, 0.003), material=black_plastic_mat, bevel_width=0.0))

    # Gaming Laptop (Oriented facing the front Y- so it faces the chair after desk rotation)
    addToDesk(create_cube("Laptop_Base", (1.05, 0.65, 0.753), (0.15, 0.11, 0.008), material=black_plastic_mat, bevel_width=0.002))
    scr = addToDesk(create_cube("Laptop_Screen", (1.05, 0.75, 0.865), (0.14, 0.008, 0.11), material=black_plastic_mat, bevel_width=0.002))
    scr.rotation_euler[0] = -0.32
    disp = addToDesk(create_cube("Laptop_Display", (1.05, 0.742, 0.865), (0.13, 0.002, 0.10), material=screen_emit_mat, bevel_width=0.0))
    disp.rotation_euler[0] = -0.32
    
    # Laptop Keyboard (integrated directly onto the laptop base on the front Y- half)
    addToDesk(create_cube("Laptop_KB_Recess", (1.05, 0.59, 0.758), (0.12, 0.045, 0.001), material=black_plastic_mat, bevel_width=0.0))
    for r in range(5):
        for c in range(10):
            kx = 1.05 - 0.099 + c * 0.022
            ky = 0.59 - 0.036 + r * 0.018
            if (r + c) % 8 == 0:
                key_col = (0.95, 0.4, 0.1, 1.0)
            else:
                key_col = (0.16, 0.16, 0.18, 1.0)
            k_mat = create_simple_material(f"LaptopKey_{r}_{c}", key_col, roughness=0.6)
            addToDesk(create_cube(f"LaptopKey_{r}_{c}", (kx, ky, 0.76), (0.009, 0.012, 0.002), material=k_mat, bevel_width=0.0005))
            
    # Mouse
    addToDesk(create_cube("Mouse", (1.18, 0.65, 0.755), (0.04, 0.024, 0.015), material=black_plastic_mat, bevel_width=0.005))

    # Detailed Anglepoise/Pixar style Desk Lamp (On the right-hand side, behind the headphones)
    # 1. Circular base sitting on the desk
    addToDesk(create_cylinder("Lamp_Base", (1.45, 0.85, 0.75), radius=0.04, depth=0.01, material=black_plastic_mat))
    # 2. Lower neck segment angled forward
    addToDesk(create_cylinder("Lamp_Neck_Lower", (1.46, 0.85, 0.84), radius=0.006, depth=0.18, rotation=(0, 0.3, 0), material=metal_mat))
    # 3. Middle elbow joint pin
    addToDesk(create_cylinder("Lamp_Joint_1", (1.485, 0.85, 0.925), radius=0.01, depth=0.016, rotation=(1.5708, 0, 0), material=black_plastic_mat))
    # 4. Upper neck segment angled forward
    addToDesk(create_cylinder("Lamp_Neck_Upper", (1.43, 0.85, 1.01), radius=0.006, depth=0.16, rotation=(0, -0.6, 0), material=metal_mat))
    # 5. Shade mounting joint pin
    addToDesk(create_cylinder("Lamp_Joint_2", (1.355, 0.85, 1.08), radius=0.008, depth=0.016, rotation=(1.5708, 0, 0), material=black_plastic_mat))
    # 6. Dome lamp shade pointing downward/forward towards the laptop (left)
    addToDesk(create_cylinder("Lamp_Shade", (1.33, 0.85, 1.05), radius=0.045, depth=0.05, rotation=(0, 0.8, 0), material=black_plastic_mat, bevel_width=0.01))
    # 7. Light bulb inside the shade (emits strong warm light)
    addToDesk(create_cylinder("Lamp_Bulb", (1.32, 0.85, 1.04), radius=0.038, depth=0.008, rotation=(0, 0.8, 0), material=strong_white_led_mat))


    
    # Translucent water bottle (moved to back right corner)
    addToDesk(create_cylinder("WaterBottle", (1.65, 0.85, 0.84), radius=0.04, depth=0.18, material=bottle_mat))
    addToDesk(create_cylinder("WaterBottle_Cap", (1.65, 0.85, 0.94), radius=0.025, depth=0.02, material=metal_mat))
    
    # Charger brick (moved to back left corner)
    addToDesk(create_cube("ChargerBrick", (0.9, 0.85, 0.75), (0.025, 0.035, 0.015), material=window_frame_mat, bevel_width=0.003))
    
    # Stack of books (Behind the laptop on the left side of the table)
    
    b1_bk = addToDesk(create_cube("DeskBook_1", (0.75, 0.88, 0.765), (0.11, 0.08, 0.03), material=book_red_mat, bevel_width=0.004))
    b1_bk.rotation_euler[2] = 0.15
    b2_bk = addToDesk(create_cube("DeskBook_2", (0.76, 0.88, 0.815), (0.1, 0.075, 0.025), material=book_teal_mat, bevel_width=0.004))
    b2_bk.rotation_euler[2] = -0.08
    b3_bk = addToDesk(create_cube("DeskBook_3", (0.74, 0.87, 0.855), (0.09, 0.07, 0.022), material=book_yellow_mat, bevel_width=0.004))
    b3_bk.rotation_euler[2] = 0.04

    # Steaming Coffee Mug & Pen Holder on Desk
    addToDesk(create_cylinder("DeskMug", (0.86, 0.55, 0.77), radius=0.026, depth=0.052, material=plant_pot_mat))
    addToDesk(create_cylinder("DeskMug_Handle", (0.84, 0.55, 0.77), radius=0.011, depth=0.01, rotation=(1.5708, 0, 0), material=plant_pot_mat))
    
    addToDesk(create_cylinder("PenHolder", (1.28, 0.55, 0.78), radius=0.024, depth=0.06, material=black_plastic_mat))
    p_blue_mat = create_simple_material("PenBlueMat", (0.1, 0.4, 0.8, 1.0), roughness=0.5)
    p_red_mat = create_simple_material("PenRedMat", (0.8, 0.1, 0.2, 1.0), roughness=0.5)
    p1_obj = create_cylinder("Pen_1", (1.27, 0.54, 0.83), radius=0.004, depth=0.1, rotation=(0.2, 0.1, 0.2), material=p_blue_mat)
    p2_obj = create_cylinder("Pen_2", (1.29, 0.56, 0.83), radius=0.004, depth=0.1, rotation=(-0.25, -0.15, -0.1), material=p_red_mat)
    addToDesk(p1_obj)
    addToDesk(p2_obj)
    
    # Hollow Dustbin (Red bucket - on the right side of the wardrobe)
    create_hollow_bucket("RedBucket", (-0.1, 1.4, 0.15), radius=0.14, depth=0.28, material=red_bucket_mat)


    # 12. Neon LED Glow Strips (desk strip is parented to rotate with desk)
    addToDesk(create_cylinder("LEDStrip_Desk", (1.2, 0.7, 0.742), radius=0.005, depth=1.2, rotation=(1.5708, 0, 0), material=cyan_led_mat))
    create_cylinder("LEDStrip_BackWall", (0.0, 1.98, 0.04), radius=0.005, depth=2.0, rotation=(0, 1.5708, 0), material=pink_led_mat)

    # Rotate the entire desk group (including all its drawers, panels, and props) by -90 degrees around Z axis so it faces X-
    desk_parent.rotation_euler[2] = -1.5708

    # 13. Orthographic Camera Setup
    camera_data = bpy.data.cameras.new(name="IsometricCamera")
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 5.2
    camera_obj = bpy.data.objects.new("IsometricCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    bpy.context.scene.camera = camera_obj
    camera_obj.location = (8.5, -8.5, 8.5)
    camera_obj.rotation_euler = (0.955324, 0.0, 0.785398) # X: 54.736, Y: 0, Z: 45 degrees
    
    # Auto-adjust viewport space to camera view and Rendered Shading mode
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    space.shading.type = 'RENDERED'

    # 14. Vibrant Cozy Lighting
    light_data_win = bpy.data.lights.new(name="WindowLight", type='AREA')
    light_data_win.energy = 220
    light_data_win.color = (0.4, 0.6, 1.0)
    light_data_win.size = 2.5
    light_win = bpy.data.objects.new("WindowLight", light_data_win)
    bpy.context.scene.collection.objects.link(light_win)
    light_win.location = (-2.5, -0.5, 1.55)
    light_win.rotation_euler = (0.0, 1.5708, 0.0)
    # Subtle warm ambient floor glow under desk
    light_data_desk = bpy.data.lights.new(name="DeskGlow", type='POINT')
    light_data_desk.energy = 25
    light_data_desk.color = (1.0, 0.5, 0.1)
    light_desk = bpy.data.objects.new("DeskGlow", light_data_desk)
    bpy.context.scene.collection.objects.link(light_desk)
    light_desk.location = (1.2, 0.7, 0.22)
    light_desk.parent = desk_parent
    light_desk.matrix_parent_inverse = desk_parent.matrix_world.inverted()
    
    # Logical Cozy Desk Lamp light casting light downwards onto the desk
    light_data_lamp = bpy.data.lights.new(name="LampLight", type='POINT')
    light_data_lamp.energy = 110
    light_data_lamp.color = (1.0, 0.9, 0.75) # cozy warm white-yellow
    light_lamp = bpy.data.objects.new("LampLight", light_data_lamp)
    bpy.context.scene.collection.objects.link(light_lamp)
    light_lamp.location = (1.32, 0.85, 1.04)
    light_lamp.parent = desk_parent
    light_lamp.matrix_parent_inverse = desk_parent.matrix_world.inverted()
    
    # Subtle accent glow under the bed
    light_data_bed = bpy.data.lights.new(name="BedGlow", type='POINT')
    light_data_bed.energy = 20
    light_data_bed.color = (1.0, 0.0, 0.4)
    light_bed = bpy.data.objects.new("BedGlow", light_data_bed)
    bpy.context.scene.collection.objects.link(light_bed)
    light_bed.location = (-1.25, -0.35, 0.12)
    
    light_data_top = bpy.data.lights.new(name="TopLight", type='AREA')
    light_data_top.energy = 35.0
    light_data_top.color = (1.0, 0.98, 0.94)
    light_data_top.size = 4.5
    light_top = bpy.data.objects.new("TopLight", light_data_top)
    bpy.context.scene.collection.objects.link(light_top)
    light_top.location = (0.0, 0.0, 4.5)
    light_top.rotation_euler = (3.14159, 0.0, 0.0)

    # 15. Render Engine Configuration
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.cycles.samples = 96
    bpy.context.scene.cycles.preview_samples = 256
    
    # Enable Viewport Denoising
    if hasattr(bpy.context, "view_layer") and hasattr(bpy.context.view_layer, "cycles"):
        bpy.context.view_layer.cycles.use_denoising = True
    
    if hasattr(bpy.context.scene.cycles, "device"):
        bpy.context.scene.cycles.device = 'GPU'
        
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
            
    if bpy.data.worlds.get("World"):
        world = bpy.data.worlds["World"]
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.04, 0.04, 0.05, 1.0)
            bg_node.inputs['Strength'].default_value = 1.0

    # 16. Bake Procedural Textures to Images for GLB/FBX Exporting
    try:
        print("Baking procedural walnut wood texture...")
        bake_wood_texture()
    except Exception as e:
        print(f"Failed to bake wood texture: {e}")

    # 17. Export Model to C:\Users\negih\Downloads\grok_try_resume
    import os
    export_dir = r"C:\Users\negih\Downloads\grok_try_resume"
    if not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir)
        except Exception:
            pass
            
    glb_path = os.path.join(export_dir, "room_model.glb")
    fbx_path = os.path.join(export_dir, "room_model.fbx")
    
    # Export GLB (with materials, lights, and cameras packaged)
    try:
        bpy.ops.export_scene.gltf(
            filepath=glb_path,
            export_format='GLB',
            use_selection=False,
            export_lights=True,
            export_cameras=True,
            export_materials='EXPORT'
        )
        print(f"Exported GLB to: {glb_path}")
    except Exception as e:
        print(f"Failed to export GLB: {e}")
        
    # Export FBX (with meshes, lights, and cameras packaged)
    try:
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=False,
            path_mode='COPY',
            embed_textures=True,
            object_types={'MESH', 'LIGHT', 'CAMERA'}
        )
        print(f"Exported FBX to: {fbx_path}")
    except Exception as e:
        print(f"Failed to export FBX: {e}")

    # 18. Bake and Export fully baked room for WebGL/Three.js (looks exactly like the render in real-time)
    try:
        print("Starting complete scene light baking for Three.js (this will take a moment)...")
        bake_and_export_combined_glb()
    except Exception as e:
        print(f"Failed to bake and export combined GLB: {e}")

    # 18. Render and save high-quality Cycles camera image
    render_path = os.path.join(export_dir, "room_render.png")
    bpy.context.scene.render.filepath = render_path
    
    orig_engine = bpy.context.scene.render.engine
    orig_samples = bpy.context.scene.cycles.samples
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    try:
        bpy.context.scene.cycles.use_denoising = True
    except AttributeError:
        pass
        
    try:
        print("Rendering high-quality image of the room...")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered image saved to: {render_path}")
    except Exception as e:
        print(f"Failed to render image: {e}")
        
    bpy.context.scene.render.engine = orig_engine
    bpy.context.scene.cycles.samples = orig_samples

    print("Isometric room generation, texture baking, and export complete!")

if __name__ == "__main__":
    build_room()
