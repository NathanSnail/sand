cbuffer Config : register(b0)
{
    int2 offset;
};

/*

config:
    offset u32 %2 == y // 2 == x

inf_array:
    density f32

inf_array:
    type u32

// col_array:
//     colour vec4<f32>

reactions:
    product arr<vec2<u32>>

world:
    mat_ids arr<u32>
*/

// 8 material types in a 65x65
RWTexture2D<uint> world : register(u0); // rw
Texture1D<float> density : register(t1); // r
Texture1D<uint> type : register(t0); // r

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy * 3 + offset;
    // if 2 sand pixels are 1 space apart they made randomly fall into the same spot for *2 causing matter deletion
    if (density[0] < 1)
    {
        world[int2(0,0)] = 0;
    }
    // world[pos] = 1;
    if (type[2] == 1010876609)
    {
        // world[pos] = 0;
    }
    world[pos] = (world[pos] + 1) % 3;
    if (type[3] < 2)
    {
        world[pos] = 0;
    }
    return;
    uint c_type = type[world[pos]];
    // if (c_type > 5)
    //     {
    //         world[pos] = 0;
    //     }
    world[pos] = type[2000];
    switch (c_type)
    {
        case 0: // air
            return;
        case 1:
            return; // TODO: gas 
        case 2: // sand
            world[pos] = 0;
            if (pos.y + 1 >= 1/*$HEIGHT*/)
            { // bottom of world
                return;
            }
            uint swap = world[int2(pos.x,pos.y+1)];
            if (density[type[swap]] < density[c_type])
            { // fall
                world[int2(pos.x,pos.y+1)] = world[pos];
                world[pos] = swap;
            }
            return;

    }
}
