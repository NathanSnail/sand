cbuffer Config : register(b0)
{
    uint offset;
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
Texture1D<float> density : register(t0); // r
Texture1D<uint> type : register(t1); // r

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy;
    if (density[0] < 1)
    {
        world[int2(0,0)] = 0;
    }
    if (type[0] < 1)
    {
        world[int2(0,0)] = 0;
    }
    world[pos] = 1 - world[pos];
}
