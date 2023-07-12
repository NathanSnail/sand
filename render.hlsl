Texture2D<uint> world : register(t0);
Texture1D<float4> colours : register(t1);
RWTexture2D<float4> target : register(u1);

[numthreads(8,8,1)]
void main(int3 global_pos : SV_DispatchThreadID)
{
    int2 pos = global_pos.xy;
    //float4 data = colours[0][0];
    // int2 scaled_pos = pos / 10;
    // scaled_pos.x = min(scaled_pos.x,20);
    // scaled_pos.y = min(scaled_pos.y,20);
    // uint world_val = world[scaled_pos]; // errors if pos too big
    uint width;
    uint height;
    // world.GetDimensions(width,height);
    target[pos] += colours[0];
    //float4 col = colours[world_val];
    //target[pos] = col;
    // if (scaled_pos.x < 100)
    // {
    target[pos] = float4(1,1,0,1);
    // }
}